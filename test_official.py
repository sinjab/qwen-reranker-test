#!/usr/bin/env python3
"""
Official Qwen3-Reranker Test
Tests the official HuggingFace implementation of Qwen3-Reranker
"""

import json
import time
import os
import glob
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def load_test_cases():
    """Load test cases from JSON files in tests/ directory"""
    test_cases = []
    test_files = glob.glob("tests/test_*.json")
    
    for test_file in sorted(test_files):
        try:
            with open(test_file, 'r') as f:
                test_data = json.load(f)
                
            # Extract test case name from filename
            test_name = os.path.splitext(os.path.basename(test_file))[0]
            
            # Create test case structure
            test_case = {
                "name": test_name,
                "file": test_file,
                "query": test_data.get("query", ""),
                "documents": test_data.get("documents", [])
            }
            
            # Add optional parameters if present
            if "instruction" in test_data:
                test_case["instruction"] = test_data["instruction"]
            if "top_n" in test_data:
                test_case["top_n"] = test_data["top_n"]
            if "model" in test_data:
                test_case["model"] = test_data["model"]
                
            test_cases.append(test_case)
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load {test_file}: {e}")
    
    return test_cases

def test_official_qwen(test_case):
    """Test official Qwen3-Reranker"""
    try:
        # Load model and tokenizer
        model_name = "Qwen/Qwen3-Reranker-0.6B"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # Fix padding token issue
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        query = test_case["query"]
        documents = test_case["documents"]
        
        # Process documents one by one to avoid batch padding issues
        results = []
        start_time = time.time()
        
        for idx, doc in enumerate(documents):
            # Tokenize single pair
            inputs = tokenizer([[query, doc]], padding=True, truncation=True, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model(**inputs)
                # Handle tensor properly - get the score from logits
                logits = outputs.logits
                if logits.dim() > 1:
                    score = logits.squeeze().tolist()
                    if isinstance(score, list):
                        score = score[0]  # Take first element if it's a list
                else:
                    score = logits.item()
            
            results.append({
                "index": idx,
                "document": doc,
                "relevance_score": score
            })
        
        elapsed = time.time() - start_time
        
        # Sort by score (descending)
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Apply top_n if specified
        if "top_n" in test_case:
            results = results[:test_case["top_n"]]
        
        return {
            "success": True,
            "results": results,
            "time": elapsed,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "time": 0,
            "error": str(e)
        }

def main():
    """Run official Qwen3-Reranker tests only"""
    print("🤖 Official Qwen3-Reranker Test")
    print("=" * 40)
    
    results = {}
    test_cases = load_test_cases()
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print(f"Documents: {len(test_case['documents'])}")
        
        # Test Official
        print("🤖 Testing Official Qwen3-Reranker...")
        official_result = test_official_qwen(test_case)
        
        results[test_case["name"]] = {
            "test_case": test_case,
            "result": official_result
        }
        
        # Print summary
        print(f"✅ Official: {'SUCCESS' if official_result['success'] else 'FAILED'} ({official_result['time']:.3f}s)")
        
        if official_result.get("error"):
            print(f"❌ Official Error: {official_result['error']}")
        
        if official_result["success"] and official_result["results"]:
            print("📈 Rankings:")
            for i, result in enumerate(official_result["results"]):
                doc = result["document"]
                score = result["relevance_score"]
                print(f"  {i+1}. {doc[:50]}... (score: {score:.4f})")
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Save results
    results_file = "results/official_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 40)
    total_tests = len(test_cases)
    successful_tests = sum(1 for r in results.values() if r["result"]["success"])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful Tests: {successful_tests}")
    print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")

if __name__ == "__main__":
    main() 