# Qwen3-Reranker Comparison

Compare Ollama implementation vs Official Qwen3-Reranker using identical JSON test cases.

## 🏗️ Project Structure

The project has been split into modular components for better organization:

- `compare_test.py` - Main entry point (wrapper script)
- `test_ollama.py` - Tests only Ollama implementation
- `test_official.py` - Tests only Official Qwen3-Reranker
- `compare_results.py` - Compares results from both implementations
- `requirements.txt` - Python dependencies
- `run_test.sh` - One-click test runner
- `Modelfile` - F16 model template
- `Qwen3-Reranker-0.6B.f16.gguf` - GGUF model file (download required)
- `tests/` - Test cases directory
  - `test_*.json` - JSON test files for manual Ollama testing
- `results/` - Generated results (not tracked in git)



## Model Download

The GGUF model file is required but not included in the repository due to size. Download it from:

```bash
wget https://huggingface.co/mradermacher/Qwen3-Reranker-0.6B-GGUF/resolve/main/Qwen3-Reranker-0.6B.f16.gguf
```

**Direct URL**: https://huggingface.co/mradermacher/Qwen3-Reranker-0.6B-GGUF/resolve/main/Qwen3-Reranker-0.6B.f16.gguf

## Quick Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download the GGUF model (if not already present)
wget https://huggingface.co/mradermacher/Qwen3-Reranker-0.6B-GGUF/resolve/main/Qwen3-Reranker-0.6B.f16.gguf

# Ensure Ollama is running with reranking model
OLLAMA_NEW_ENGINE=1 ollama serve
ollama create qwen_reranker_v2 -f Modelfile  # F16 model required
```

## 🚀 Running Tests

### Option 1: Run Everything (Recommended)
```bash
python compare_test.py
```

### Option 2: Run Individual Components
```bash
# Test only Ollama implementation
python test_ollama.py

# Test only Official implementation  
python test_official.py

# Compare existing results
python compare_results.py
```

### Option 3: One-click runner
```bash
./run_test.sh
```

### Option 4: Manual Ollama testing
```bash
# Test individual JSON files
curl -X POST http://localhost:11434/api/rerank -H "Content-Type: application/json" -d @tests/test_capital.json
curl -X POST http://localhost:11434/api/rerank -H "Content-Type: application/json" -d @tests/test_ml.json
curl -X POST http://localhost:11434/api/rerank -H "Content-Type: application/json" -d @tests/test_cooking.json
```

## 📋 Test Cases

Uses the same JSON test cases as the Ollama implementation:

1. **Capital Test**: "What is the capital of China?" - Beijing should rank #1
2. **ML Test**: "What is machine learning?" - AI content should rank higher  
3. **Cooking Test**: "How to cook pasta?" - Recipe should rank #1
4. **Empty Test**: Error handling for empty documents
5. **Invalid Test**: Error handling for invalid inputs

## 📈 Expected Output

```
📋 Testing: test_capital
⚡ Testing Ollama... ✅ SUCCESS (0.671s)
🤖 Testing Official... ✅ SUCCESS (0.417s)
🎯 Ranking Match: NO
📊 Score Similarity: 0.989

📈 Rankings:
Ollama:   ['1. The capital of China is Beijin...', '2. Paris is the capital of F...']
Official: ['1. The capital of China is Beijin...', '2. China is a large country...']
```

## 📁 Files Generated

- `results/ollama_results.json` - Ollama test results
- `results/official_results.json` - Official test results  
- `results/comparison_results.json` - Detailed comparison results

## ✅ Success Criteria

- ✅ Both implementations succeed
- ✅ Rankings match (same document order)
- ✅ Score similarity >0.8
- ✅ Ollama faster than official implementation

## 🔍 Key Findings

### Strengths
- **High Score Similarity**: Even when rankings differ, score similarity is very high (0.989-1.000)
- **Fast Performance**: Both implementations are reasonably fast
- **Consistent Behavior**: Most tests produce consistent results

### Areas for Investigation
- **Ranking Differences**: Some tests show different ranking orders despite high score similarity
- **Error Handling**: Ollama fails on empty documents while Official handles them gracefully
- **Model Initialization**: Official model shows initialization warnings

### Performance Notes
- **No absolute paths required** - All files are relative to the test directory
- Ollama implementation is generally faster
- Official Qwen requires ~2GB GPU memory
- Slight score differences are normal due to implementation details
- Focus is on ranking order, not exact score matching

## JSON Test Files

The `tests/` directory includes pre-made JSON test files for manual testing:
- `tests/test_capital.json` - Capital query test
- `tests/test_ml.json` - Machine learning test with instruction
- `tests/test_cooking.json` - Cooking test with top_n limit
- `tests/test_empty.json` - Error test (empty documents)
- `tests/test_invalid.json` - Error test (invalid model)

## 🔧 Troubleshooting

### Common Issues
1. **Ollama not running**: Ensure `ollama serve` is running
2. **Model not found**: Download the GGUF model file
3. **CUDA errors**: Official implementation requires GPU memory
4. **Empty document errors**: Ollama doesn't handle empty document arrays well

### Debug Mode
Run individual components to isolate issues:
```bash
python test_ollama.py      # Debug Ollama issues
python test_official.py    # Debug Official issues
```
