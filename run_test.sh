#!/bin/bash
# Test runner for Qwen3-Reranker comparison

echo "🚀 Qwen3-Reranker Comparison Test"
echo "================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.7+"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama not running. Please start Ollama first:"
    echo "   OLLAMA_NEW_ENGINE=1 ollama serve"
    exit 1
fi

# Check if qwen_reranker_v2 model exists
if ! curl -s http://localhost:11434/api/show -d '{"name":"qwen_reranker_v2"}' 2>/dev/null | grep -q "qwen_reranker_v2"; then
    echo "❌ qwen_reranker_v2 model not found. Please create it first:"
    echo "   ./ollama create qwen_reranker_v2 -f Modelfile"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Install requirements if needed
if ! python3 -c "import torch, transformers, requests" 2>/dev/null; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    echo ""
fi

# Run the test
echo "🧪 Running comparison test..."
python3 compare_test.py

echo ""
echo "✨ Test complete! Check comparison_results.json for detailed results."
