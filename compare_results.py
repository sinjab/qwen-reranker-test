#!/usr/bin/env python3
"""
Qwen3-Reranker Comparison Test Suite
===================================

Compares Ollama and official Qwen3-Reranker implementations side-by-side.
This comparison revealed the fundamental differences between the implementations
and led to the discovery of the correct approach.

Key Discovery: The huge differences were due to Ollama using text generation
with numeric parsing, while the official implementation uses binary classification
with logit probabilities.

Usage:
    python compare_results.py

Results:
    - Saves detailed comparison to results/comparison_results.json
    - Shows ranking matches and score similarities
    - Highlights implementation differences
"""

import json
import os
import glob
import subprocess
import sys

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

def run_tests():
    """Run both test scripts"""
    print("🚀 Running Ollama tests...")
    try:
        subprocess.run([sys.executable, "test_ollama.py"], check=True)
        print("✅ Ollama tests completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ollama tests failed: {e}")
        return False
    
    print("\n🚀 Running Official tests...")
    try:
        subprocess.run([sys.executable, "test_official.py"], check=True)
        print("✅ Official tests completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Official tests failed: {e}")
        return False
    
    return True

def load_results():
    """Load results from JSON files"""
    ollama_results = {}
    official_results = {}
    
    # Load Ollama results
    if os.path.exists("results/ollama_results.json"):
        with open("results/ollama_results.json", 'r') as f:
            ollama_data = json.load(f)
            for test_name, data in ollama_data.items():
                ollama_results[test_name] = data["result"]
    
    # Load Official results
    if os.path.exists("results/official_results.json"):
        with open("results/official_results.json", 'r') as f:
            official_data = json.load(f)
            for test_name, data in official_data.items():
                official_results[test_name] = data["result"]
    
    return ollama_results, official_results

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
    
    # Check if results exist
    ollama_exists = os.path.exists("results/ollama_results.json")
    official_exists = os.path.exists("results/official_results.json")
    
    if not ollama_exists or not official_exists:
        print("📋 Running tests first...")
        if not run_tests():
            print("❌ Failed to run tests. Exiting.")
            return
    else:
        print("📋 Using existing results...")
    
    # Load results
    ollama_results, official_results = load_results()
    
    if not ollama_results or not official_results:
        print("❌ No results found. Please run tests first.")
        return
    
    # Get test cases for reference
    test_cases = load_test_cases()
    test_case_map = {tc["name"]: tc for tc in test_cases}
    
    # Compare results
    comparison_results = {}
    
    for test_name in test_case_map.keys():
        if test_name in ollama_results and test_name in official_results:
            print(f"\n📋 Comparing: {test_name}")
            print(f"Query: {test_case_map[test_name]['query']}")
            print(f"Documents: {len(test_case_map[test_name]['documents'])}")
            
            ollama_result = ollama_results[test_name]
            official_result = official_results[test_name]
            
            # Compare results
            comparison = compare_results(ollama_result, official_result)
            
            comparison_results[test_name] = {
                "test_case": test_case_map[test_name],
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
    
    # Save comparison results
    results_file = "results/comparison_results.json"
    with open(results_file, "w") as f:
        json.dump(comparison_results, f, indent=2)
    
    print(f"\n💾 Comparison results saved to: {results_file}")
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 50)
    total_tests = len(comparison_results)
    successful_tests = sum(1 for r in comparison_results.values() if r["ollama"]["success"] and r["official"]["success"])
    ranking_matches = sum(1 for r in comparison_results.values() if r["comparison"]["ranking_match"])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful Tests: {successful_tests}")
    print(f"Ranking Matches: {ranking_matches}")
    print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
    print(f"Ranking Match Rate: {ranking_matches/successful_tests*100:.1f}%" if successful_tests > 0 else "Ranking Match Rate: N/A")

if __name__ == "__main__":
    main() 