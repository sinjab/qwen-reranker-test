#!/usr/bin/env python3
"""
Ollama Qwen3-Reranker Test
Tests Ollama's implementation of Qwen3-Reranker
"""

import json
import requests
import time
import os
import glob

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

def main():
    """Run Ollama tests only"""
    print("🧪 Ollama Qwen3-Reranker Test")
    print("=" * 40)
    
    results = {}
    test_cases = load_test_cases()
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print(f"Documents: {len(test_case['documents'])}")
        
        # Test Ollama
        print("⚡ Testing Ollama...")
        ollama_result = test_ollama_reranker(test_case)
        
        results[test_case["name"]] = {
            "test_case": test_case,
            "result": ollama_result
        }
        
        # Print summary
        print(f"✅ Ollama: {'SUCCESS' if ollama_result['success'] else 'FAILED'} ({ollama_result['time']:.3f}s)")
        
        if ollama_result.get("error"):
            print(f"❌ Ollama Error: {ollama_result['error']}")
        
        if ollama_result["success"] and ollama_result["results"]:
            print("📈 Rankings:")
            for i, result in enumerate(ollama_result["results"]):
                doc = result["document"]
                score = result["relevance_score"]
                print(f"  {i+1}. {doc[:50]}... (score: {score:.4f})")
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Save results
    results_file = "results/ollama_results.json"
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