#!/usr/bin/env python3
"""
Ambiguous Case Testing - Real Official Implementation
===================================================

Test ambiguous cases with the real Qwen3-Reranker using Transformers.
This provides the ground truth for comparison with Ollama's implementation.
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

def test_ambiguous_cases():
    """Test ambiguous cases with real implementation"""
    print("🧪 AMBIGUOUS CASE TESTING - REAL OFFICIAL")
    print("=" * 60)
    
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
    
    # Define ambiguous test cases
    test_cases = [
        {
            "name": "Ambiguous Technology Query",
            "query": "How to improve software performance?",
            "documents": [
                "Optimize database queries for faster execution.",
                "Use caching mechanisms to reduce load times.",
                "Upgrade hardware components like RAM and CPU.",
                "Write efficient algorithms and data structures.",
                "Clean your computer screen regularly."
            ]
        },
        {
            "name": "Partial Relevance",
            "query": "Best restaurants in Paris",
            "documents": [
                "Paris has many excellent bistros and cafes.",
                "French cuisine is known for its sophistication.",
                "Booking tables in advance is recommended.",
                "Le Bernardin is a famous French restaurant in New York.",
                "The Eiffel Tower is a popular tourist attraction."
            ]
        },
        {
            "name": "Subtle Differences",
            "query": "Climate change effects",
            "documents": [
                "Global warming is causing ice caps to melt.",
                "Weather patterns are becoming more unpredictable.",
                "Rising sea levels threaten coastal cities.",
                "Environmental protection is important for future generations.",
                "My cat likes to sleep in the sun."
            ]
        },
        {
            "name": "Technical Ambiguity",
            "query": "Machine learning optimization",
            "documents": [
                "Gradient descent is an optimization algorithm.",
                "Hyperparameter tuning improves model performance.",
                "Neural networks require careful tuning.",
                "Coffee helps programmers stay awake.",
                "Deep learning models need large datasets."
            ]
        }
    ]
    
    task = 'Given a web search query, retrieve relevant passages that answer the query'
    
    for test_case in test_cases:
        print(f"\n🔍 {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print("-" * 40)
        
        query = test_case["query"]
        documents = test_case["documents"]
        
        pairs = [format_instruction(task, query, doc) for doc in documents]
        
        # Tokenize the input texts
        inputs = process_inputs(pairs, tokenizer, prefix_tokens, suffix_tokens, max_length, model)
        scores = compute_logits(inputs, model, token_true_id, token_false_id)
        
        # Show results with documents
        for i, (doc, score) in enumerate(zip(documents, scores)):
            print(f"  {i+1}. [{score:.4f}] {doc[:50]}...")
            
    print("\n" + "=" * 60)
    print("🎯 These are the REAL official scores for ambiguous cases!")

if __name__ == "__main__":
    test_ambiguous_cases()
