#!/usr/bin/env python3
"""
Real Official Qwen3-Reranker Implementation Test
==============================================

This script tests the ACTUAL official Qwen3-Reranker model using the
Transformers library, providing the ground truth for comparison with
Ollama's implementation.

Key Discovery: The Qwen3-Reranker uses binary classification (yes/no)
with logit probabilities, NOT numeric scoring as initially assumed.

Usage:
    python scripts/test_real_official.py

Requirements:
    - torch
    - transformers>=4.51.0
    - Qwen/Qwen3-Reranker-0.6B model (downloaded automatically)
"""

import torch
from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM

def format_instruction(instruction, query, doc):
    if instruction is None:
        instruction = 'Given a web search query, retrieve relevant passages that answer the query'
    output = "<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}".format(instruction=instruction,query=query, doc=doc)
    return output

def process_inputs(pairs, tokenizer, prefix_tokens, suffix_tokens, max_length, model):
    inputs = tokenizer(
        pairs, padding=False, truncation='longest_first',
        return_attention_mask=False, max_length=max_length - len(prefix_tokens) - len(suffix_tokens)
    )
    for i, ele in enumerate(inputs['input_ids']):
        inputs['input_ids'][i] = prefix_tokens + ele + suffix_tokens
    inputs = tokenizer.pad(inputs, padding=True, return_tensors="pt", max_length=max_length)
    for key in inputs:
        inputs[key] = inputs[key].to(model.device)
    return inputs

def compute_logits(inputs, model, token_true_id, token_false_id, **kwargs):
    batch_scores = model(**inputs).logits[:, -1, :]
    true_vector = batch_scores[:, token_true_id]
    false_vector = batch_scores[:, token_false_id]
    batch_scores = torch.stack([false_vector, true_vector], dim=1)
    batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
    scores = batch_scores[:, 1].exp().tolist()
    return scores

def test_real_official():
    """Test with the real official implementation"""
    print("🤖 REAL OFFICIAL QWEN3-RERANKER TEST")
    print("=" * 50)
    
    # Load the real model
    print("📦 Loading real Qwen3-Reranker model...")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Reranker-0.6B", padding_side='left')
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-Reranker-0.6B").eval()
    
    token_false_id = tokenizer.convert_tokens_to_ids("no")
    token_true_id = tokenizer.convert_tokens_to_ids("yes")
    max_length = 8192
    prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
    suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
    prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
    suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)
    
    print("✅ Model loaded successfully!")
    print(f"🎯 Token IDs: false={token_false_id}, true={token_true_id}")
    
    # Test our standard test cases
    test_cases = [
        {
            "name": "Capital Test",
            "queries": ["What is the capital of China?", "What is the capital of China?", "What is the capital of China?"],
            "documents": [
                "The capital of China is Beijing.",
                "China is a large country in Asia.",
                "Paris is the capital of France."
            ]
        },
        {
            "name": "ML Test",
            "queries": ["What is machine learning?", "What is machine learning?", "What is machine learning?"],
            "documents": [
                "Machine learning is a subset of artificial intelligence.",
                "The weather today is sunny.",
                "Deep learning uses neural networks."
            ]
        },
        {
            "name": "Basic Example",
            "queries": ["What is the capital of China?", "Explain gravity"],
            "documents": [
                "The capital of China is Beijing.",
                "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun."
            ]
        }
    ]
    
    task = 'Given a web search query, retrieve relevant passages that answer the query'
    
    for test_case in test_cases:
        print(f"\n🔍 {test_case['name']}")
        print("-" * 30)
        
        queries = test_case["queries"]
        documents = test_case["documents"]
        
        pairs = [format_instruction(task, query, doc) for query, doc in zip(queries, documents)]
        
        # Show the formatted instruction for first pair
        print(f"📝 Sample formatted instruction:")
        print(f"   {pairs[0][:100]}...")
        
        # Tokenize the input texts
        inputs = process_inputs(pairs, tokenizer, prefix_tokens, suffix_tokens, max_length, model)
        scores = compute_logits(inputs, model, token_true_id, token_false_id)
        
        print(f"📊 Scores: {scores}")
        
        # Show results with documents
        for i, (query, doc, score) in enumerate(zip(queries, documents, scores)):
            print(f"  {i+1}. [{score:.4f}] {doc[:50]}...")
            
    print("\n" + "=" * 50)
    print("🎯 These are the REAL official scores!")

if __name__ == "__main__":
    test_real_official()
