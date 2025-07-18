#!/usr/bin/env python3
"""
Test ambiguous/uncertain cases with Ollama
"""

import json
import requests
import time

def test_ambiguous_ollama():
    """Test ambiguous cases with Ollama"""
    
    # Test cases with varying degrees of relevance
    test_cases = [
        {
            "name": "Ambiguous Technology Query",
            "query": "How to improve software performance?",
            "documents": [
                "Optimize database queries for faster execution.",
                "Use caching mechanisms to reduce load times.",
                "Clean your computer screen regularly.",
                "Upgrade hardware components like RAM and CPU.",
                "Write efficient algorithms and data structures."
            ]
        },
        {
            "name": "Partial Relevance",
            "query": "Best restaurants in Paris",
            "documents": [
                "Le Bernardin is a famous French restaurant in New York.",
                "Paris has many excellent bistros and cafes.",
                "The Eiffel Tower is a popular tourist attraction.",
                "French cuisine is known for its sophistication.",
                "Booking tables in advance is recommended."
            ]
        },
        {
            "name": "Subtle Differences",
            "query": "Climate change effects",
            "documents": [
                "Global warming is causing ice caps to melt.",
                "Weather patterns are becoming more unpredictable.",
                "My cat likes to sleep in the sun.",
                "Rising sea levels threaten coastal cities.",
                "Environmental protection is important for future generations."
            ]
        },
        {
            "name": "Technical Ambiguity",
            "query": "Machine learning optimization",
            "documents": [
                "Gradient descent is an optimization algorithm.",
                "Neural networks require careful tuning.",
                "Coffee helps programmers stay awake.",
                "Deep learning models need large datasets.",
                "Hyperparameter tuning improves model performance."
            ]
        }
    ]
    
    print("🧪 AMBIGUOUS CASE TESTING - OLLAMA")
    print("=" * 60)
    
    url = "http://localhost:11434/api/rerank"
    
    for test_case in test_cases:
        print(f"\n🔍 {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print("-" * 40)
        
        payload = {
            "model": "qwen_reranker_v2",
            "query": test_case["query"],
            "documents": test_case["documents"]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Display results
            for i, res in enumerate(result.get("results", [])):
                doc = res["document"]
                score = res["relevance_score"]
                print(f"  {i+1}. [{score:.2f}] {doc[:50]}...")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Look for intermediate scores and compare with official results")

if __name__ == "__main__":
    test_ambiguous_ollama()
