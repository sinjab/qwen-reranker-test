# Qwen3-Reranker Comparison

Compare Ollama implementation vs Official Qwen3-Reranker using identical JSON test cases.

## Files

- `compare_test.py` - Main comparison script
- `requirements.txt` - Python dependencies
- `run_test.sh` - One-click test runner
- `Modelfile` - F16 model template
- `Qwen3-Reranker-0.6B.f16.gguf` - GGUF model file
- `test_*.json` - JSON test files for manual Ollama testing

## Quick Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running with reranking model
OLLAMA_NEW_ENGINE=1 ollama serve
ollama create qwen_reranker_v2 -f Modelfile  # F16 model required
```

## Run Test

**Option 1: One-click runner**
```bash
./run_test.sh
```

**Option 2: Manual**
```bash
python3 compare_test.py
```

**Option 3: Manual Ollama testing**
```bash
# Test individual JSON files
curl -X POST http://localhost:11434/api/rerank -H "Content-Type: application/json" -d @test_capital.json
curl -X POST http://localhost:11434/api/rerank -H "Content-Type: application/json" -d @test_ml.json
curl -X POST http://localhost:11434/api/rerank -H "Content-Type: application/json" -d @test_cooking.json
```

## Test Cases

Uses the same JSON test cases as the Ollama implementation:

1. **Capital Test**: "What is the capital of China?" - Beijing should rank #1
2. **ML Test**: "What is machine learning?" - AI content should rank higher  
3. **Cooking Test**: "How to cook pasta?" - Recipe should rank #1

## Expected Output

```
📋 Testing: capital_test
⚡ Testing Ollama... ✅ SUCCESS (0.089s)
🤖 Testing Official... ✅ SUCCESS (0.445s)
🎯 Ranking Match: YES
📊 Score Similarity: 0.892
```

## Files Generated

- `comparison_results.json` - Detailed comparison results

## Success Criteria

- ✅ Both implementations succeed
- ✅ Rankings match (same document order)
- ✅ Score similarity >0.8
- ✅ Ollama faster than official implementation

## Notes

- **No absolute paths required** - All files are relative to the test directory
- Ollama implementation should be ~3-5x faster
- Official Qwen requires ~2GB GPU memory
- Slight score differences are normal due to implementation details
- Focus is on ranking order, not exact score matching

## JSON Test Files

The directory includes pre-made JSON test files for manual testing:
- `test_capital.json` - Capital query test
- `test_ml.json` - Machine learning test with instruction
- `test_cooking.json` - Cooking test with top_n limit
- `test_empty.json` - Error test (empty documents)
- `test_invalid.json` - Error test (invalid model)
