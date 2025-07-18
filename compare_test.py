#!/usr/bin/env python3
"""
Qwen3-Reranker Comparison Test - Main Entry Point
This is a wrapper that calls the modular comparison scripts
"""

import subprocess
import sys

def main():
    """Main entry point - runs the comparison script"""
    print("🧪 Qwen3-Reranker Comparison Test")
    print("=" * 50)
    print("This script has been split into modular components:")
    print("• test_ollama.py - Test Ollama implementation")
    print("• test_official.py - Test Official implementation") 
    print("• compare_results.py - Compare results from both")
    print("\nRunning comparison script...")
    
    try:
        subprocess.run([sys.executable, "compare_results.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Comparison failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
