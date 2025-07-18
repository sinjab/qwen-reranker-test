#!/usr/bin/env python3
"""
Official Qwen3-Reranker Test using GGUF Model
Tests the GGUF model directly using llama-cpp-python
"""

import json
import time
import os
import glob
from llama_cpp import Llama
import numpy as np

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

def load_gguf_model():
    """Load GGUF model once"""
    model_path = "Qwen3-Reranker-0.6B.f16.gguf"
    if not os.path.exists(model_path):
        return None, f"GGUF model file not found: {model_path}"
    
    try:
        model = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context window
            n_threads=4,  # Number of CPU threads
            n_gpu_layers=0,  # Use CPU only for now
            verbose=False
        )
        return model, None
    except Exception as e:
        return None, str(e)

def test_official_qwen(test_case, model):
    """Test GGUF Qwen3-Reranker"""
    try:
        query = test_case["query"]
        documents = test_case["documents"]
        
        # Handle empty documents case
        if not documents:
            return {
                "success": True,
                "results": [],
                "time": 0,
                "error": None
            }
        
        # Process documents one by one
        results = []
        start_time = time.time()
        
        for idx, doc in enumerate(documents):
            # Create prompt for reranking (similar to Modelfile template)
            prompt = f"""Query: {query}
Document: {doc}
Relevance score (0-10):"""
            
            # Generate response
            response = model(
                prompt,
                max_tokens=10,  # We only need a short response
                temperature=0.0,  # Deterministic output
                stop=["<|im_start|>", "<|im_end|>", "\n"],  # Stop tokens
                echo=False
            )
            
            # Extract score from response
            response_text = response['choices'][0]['text'].strip()
            
            # Try to extract numeric score
            try:
                # Look for numbers in the response
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', response_text)
                if numbers:
                    score = float(numbers[0])
                    # Normalize to 0-1 range if needed
                    if score > 1:
                        score = score / 10.0
                else:
                    # Fallback: use response length as proxy
                    score = len(response_text) / 100.0
            except:
                # Fallback score
                score = 0.5
            
            results.append({
                "index": idx,
                "document": doc,
                "relevance_score": score,
                "raw_response": response_text
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
    """Run GGUF Qwen3-Reranker tests only"""
    print("🤖 GGUF Qwen3-Reranker Test")
    print("=" * 40)
    
    # Load model once
    print("📦 Loading GGUF model...")
    model, error = load_gguf_model()
    if error:
        print(f"❌ Failed to load model: {error}")
        return
    
    print("✅ Model loaded successfully")
    
    results = {}
    test_cases = load_test_cases()
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print(f"Documents: {len(test_case['documents'])}")
        
        # Test GGUF
        print("🤖 Testing GGUF Qwen3-Reranker...")
        gguf_result = test_official_qwen(test_case, model)
        
        results[test_case["name"]] = {
            "test_case": test_case,
            "result": gguf_result
        }
        
        # Print summary
        print(f"✅ GGUF: {'SUCCESS' if gguf_result['success'] else 'FAILED'} ({gguf_result['time']:.3f}s)")
        
        if gguf_result.get("error"):
            print(f"❌ GGUF Error: {gguf_result['error']}")
        
        if gguf_result["success"] and gguf_result["results"]:
            print("📈 Rankings:")
            for i, result in enumerate(gguf_result["results"]):
                doc = result["document"]
                score = result["relevance_score"]
                raw_response = result.get("raw_response", "")
                print(f"  {i+1}. {doc[:50]}... (score: {score:.4f})")
                if raw_response:
                    print(f"     Raw: {raw_response}")
    
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