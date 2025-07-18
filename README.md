# Qwen3-Reranker Test Suite

This test suite was used to debug and validate the Ollama reranking implementation, leading to the discovery of the correct approach for the Qwen3-Reranker model.

## 🔍 Key Discoveries

### **Root Cause Found**
The original implementation had a fundamental misunderstanding of how the Qwen3-Reranker model works:

- **Wrong Approach**: Using text generation with numeric scoring (0-10 scale)
- **Correct Approach**: Using binary classification with yes/no responses and logit probabilities

### **Template Format**
The correct template format matches the official Transformers implementation:

```
<|im_start|>system
Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>
<|im_start|>user
<Instruct>: {{ .Instruction }}
<Query>: {{ .Query }}
<Document>: {{ .Document }}<|im_end|>
<|im_start|>assistant
<think>

</think>

```

## 📁 Directory Structure

```
├── examples/                    # Model configuration examples
│   ├── Qwen3-Reranker-Original.Modelfile     # Original (incorrect) format
│   └── Qwen3-Reranker-Corrected.Modelfile    # Corrected format
├── scripts/                     # Test and validation scripts
│   ├── test_real_official.py    # Test with real Transformers implementation
│   ├── test_ambiguous_official.py  # Test edge cases (official)
│   └── test_ambiguous_ollama.py    # Test edge cases (Ollama)
├── tests/                       # Test case definitions
│   ├── test_capital.json        # Basic capital query test
│   ├── test_cooking.json        # Cooking instructions test
│   ├── test_empty.json          # Empty documents test
│   ├── test_invalid.json        # Invalid model test
│   └── test_ml.json             # Machine learning test
├── results/                     # Test results and comparisons
├── compare_results.py           # Compare Ollama vs official results
├── compare_test.py              # Combined test runner
├── test_official.py             # Test with llama-cpp-python
├── test_ollama.py              # Test with Ollama API
└── run_test.sh                 # Automated test runner
```

## 🚀 Quick Start

### 1. Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download model (if testing locally)
curl -L -o Qwen3-Reranker-0.6B.f16.gguf https://huggingface.co/mradermacher/Qwen3-Reranker-0.6B-GGUF/resolve/main/Qwen3-Reranker-0.6B.f16.gguf
```

### 2. Test with Real Official Implementation
```bash
# Test with actual Transformers model
python scripts/test_real_official.py
```

### 3. Test with Ollama
```bash
# Start Ollama server with corrected model
ollama create qwen3-reranker -f examples/Qwen3-Reranker-Corrected.Modelfile

# Run Ollama tests
python test_ollama.py
```

### 4. Compare Results
```bash
# Run comprehensive comparison
python compare_results.py
```

## 📊 Test Results Summary

### **Before Fix**
- **Rankings**: Completely wrong (weather ranked #1 for ML queries)
- **Scores**: Inconsistent floating-point values (4.47, 5.45, etc.)
- **Approach**: Text generation with numeric parsing

### **After Fix**
- **Rankings**: Correct (matches official implementation)
- **Scores**: Proper probability values (0.0001, 0.9995, etc.)
- **Approach**: Binary classification with logit probabilities

### **Performance**
- **Ollama**: ~0.15s per query (2-3x faster than official)
- **Official**: ~0.4-0.9s per query
- **Accuracy**: 100% ranking match when properly implemented

## 🔬 Test Cases

### **Basic Tests**
- `test_capital.json`: "What is the capital of China?" → Beijing should rank #1
- `test_ml.json`: "What is machine learning?" → ML definition should rank #1, not weather

### **Edge Cases**
- `test_empty.json`: Empty document list
- `test_invalid.json`: Non-existent model
- `test_cooking.json`: Multi-step instructions

### **Ambiguous Cases**
- Technology queries with mixed relevance
- Partial relevance scenarios
- Subtle semantic differences

## 🎯 Key Learnings

1. **Model Architecture**: Qwen3-Reranker is a binary classifier, not a scorer
2. **Template Importance**: Exact template format is crucial for correct behavior
3. **GGUF Limitations**: GGUF conversion quality affects results significantly
4. **Debugging Value**: Comparative testing revealed the fundamental issue

## 📝 Notes

- The test suite requires the actual model file (1.2GB) which is not included in the repo
- Virtual environment (`venv/`) and cache files are gitignored
- Test results are saved to `results/` directory for analysis
- All test scripts support both official and Ollama implementations

## 🔧 Implementation Status

✅ **Framework**: Correct implementation approach identified  
✅ **Template**: Proper format documented and tested  
✅ **API**: Ollama reranking API working correctly  
❓ **Model Quality**: Depends on GGUF conversion quality  

This test suite serves as validation for the corrected Ollama reranking implementation and documents the debugging process that led to the solution.
