#!/usr/bin/env python3
"""
Test ambiguous/uncertain cases for reranker
"""

import json
import time
import os
from llama_cpp import Llama

def test_ambiguous_cases():
    """Test cases where reranker might be uncertain"""
    
    # Load model
    model_path = "Qwen3-Reranker-0.6B.f16.gguf"
    model = Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=4,
        n_gpu_layers=0,
        verbose=False
    )
    
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
    
    print("🧪 AMBIGUOUS CASE TESTING - OFFICIAL")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n🔍 {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print("-" * 40)
        
        results = []
        for idx, doc in enumerate(test_case['documents']):
            # Create prompt (same as Modelfile template)
            prompt = f"""Query: {test_case['query']}
Document: {doc}
Relevance score (0-10):"""
            
            # Generate response
            response = model(
                prompt,
                max_tokens=10,
                temperature=0.0,
                stop=["<|im_start|>", "<|im_end|>", "\n"],
                echo=False
            )
            
            # Extract score
            raw_text = response['choices'][0]['text'].strip()
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', raw_text)
            
            if numbers:
                score = float(numbers[0])
                if score > 1:
                    score = score / 10.0
            else:
                score = 0.0
            
            results.append({
                'index': idx,
                'document': doc,
                'score': score,
                'raw': raw_text
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Display results
        for i, result in enumerate(results):
            print(f"  {i+1}. [{result['score']:.2f}] {result['document'][:50]}...")
            print(f"      Raw: '{result['raw']}'")
    
    print("\n" + "=" * 60)
    print("🎯 Look for intermediate scores (not just 0.0 or 1.0)")

if __name__ == "__main__":
    test_ambiguous_cases()
