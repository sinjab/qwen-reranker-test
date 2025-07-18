#!/usr/bin/env python3
"""
Qwen3-Reranker comparison test
Compares Ollama implementation vs Official Qwen3-Reranker using same JSON test cases
"""

import json
import requests
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

def test_ollama_reranker(test_case):
    """Test Ollama reranking API"""
    url = "http://localhost:11434/api/rerank"
    
    payload = {
        "model": "qwen_reranker_v2",
        "query": test_case["query"],
        "documents": test_case["documents"]
    }
    
    # Add optional parameters
    if "instruction" in test_case:
        payload["instruction"] = test_case["instruction"]
    if "top_n" in test_case:
        payload["top_n"] = test_case["top_n"]
    
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "results": result.get("results", []),
            "time": elapsed,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "time": time.time() - start_time,
            "error": str(e)
        }

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

def compare_results(ollama_result, official_result):
    """Compare results from both implementations"""
    if not ollama_result["success"] or not official_result["success"]:
        return {
            "ranking_match": False,
            "score_similarity": 0,
            "errors": {
                "ollama": ollama_result.get("error"),
                "official": official_result.get("error")
            }
        }
    
    ollama_docs = [r["document"] for r in ollama_result["results"]]
    official_docs = [r["document"] for r in official_result["results"]]
    
    # Check if ranking order matches
    ranking_match = ollama_docs == official_docs
    
    # Calculate score similarity (if both have results)
    score_similarity = 0
    if ollama_result["results"] and official_result["results"]:
        ollama_scores = [r["relevance_score"] for r in ollama_result["results"]]
        official_scores = [r["relevance_score"] for r in official_result["results"]]
        
        # Normalize scores to 0-1 range for comparison
        if len(ollama_scores) == len(official_scores):
            ollama_norm = [(s - min(ollama_scores)) / (max(ollama_scores) - min(ollama_scores)) if max(ollama_scores) != min(ollama_scores) else 0 for s in ollama_scores]
            official_norm = [(s - min(official_scores)) / (max(official_scores) - min(official_scores)) if max(official_scores) != min(official_scores) else 0 for s in official_scores]
            
            score_similarity = sum(abs(a - b) for a, b in zip(ollama_norm, official_norm)) / len(ollama_norm)
            score_similarity = 1 - score_similarity  # Convert to similarity (higher is better)
    
    return {
        "ranking_match": ranking_match,
        "score_similarity": score_similarity,
        "ollama_ranking": ollama_docs,
        "official_ranking": official_docs,
        "performance": {
            "ollama_time": ollama_result["time"],
            "official_time": official_result["time"]
        }
    }

def main():
    print("🧪 Qwen3-Reranker Comparison Test")
    print("=" * 50)
    
    results = {}
    
    test_cases = load_test_cases()
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print(f"Documents: {len(test_case['documents'])}")
        
        # Test Ollama
        print("⚡ Testing Ollama...")
        ollama_result = test_ollama_reranker(test_case)
        
        # Test Official
        print("🤖 Testing Official Qwen3-Reranker...")
        official_result = test_official_qwen(test_case)
        
        # Compare results
        comparison = compare_results(ollama_result, official_result)
        
        results[test_case["name"]] = {
            "test_case": test_case,
            "ollama": ollama_result,
            "official": official_result,
            "comparison": comparison
        }
        
        # Print summary
        print(f"✅ Ollama: {'SUCCESS' if ollama_result['success'] else 'FAILED'} ({ollama_result['time']:.3f}s)")
        print(f"✅ Official: {'SUCCESS' if official_result['success'] else 'FAILED'} ({official_result['time']:.3f}s)")
        
        if ollama_result["success"] and official_result["success"]:
            print(f"🎯 Ranking Match: {'YES' if comparison['ranking_match'] else 'NO'}")
            print(f"📊 Score Similarity: {comparison['score_similarity']:.3f}")
            
            print("\n📈 Rankings:")
            print("Ollama:  ", [f"{i+1}. {doc[:30]}..." for i, doc in enumerate(comparison["ollama_ranking"])])
            print("Official:", [f"{i+1}. {doc[:30]}..." for i, doc in enumerate(comparison["official_ranking"])])
        
        if ollama_result.get("error"):
            print(f"❌ Ollama Error: {ollama_result['error']}")
        if official_result.get("error"):
            print(f"❌ Official Error: {official_result['error']}")
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Save results
    results_file = "results/comparison_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 50)
    total_tests = len(test_cases)
    successful_tests = sum(1 for r in results.values() if r["ollama"]["success"] and r["official"]["success"])
    ranking_matches = sum(1 for r in results.values() if r["comparison"]["ranking_match"])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful Tests: {successful_tests}")
    print(f"Ranking Matches: {ranking_matches}")
    print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
    print(f"Ranking Match Rate: {ranking_matches/successful_tests*100:.1f}%" if successful_tests > 0 else "Ranking Match Rate: N/A")

if __name__ == "__main__":
    main()
