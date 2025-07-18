#!/usr/bin/env python3
"""
Show current model configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Show current configuration"""
    print("🔧 Qwen3-Reranker Configuration")
    print("=" * 40)
    
    model_name = os.getenv("MODEL_NAME", "qwen_reranker_v2")
    print(f"Model Name: {model_name}")
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file found")
        with open(".env", "r") as f:
            print("📄 .env contents:")
            for line in f:
                print(f"   {line.strip()}")
    else:
        print("⚠️  .env file not found, using default model name")
    
    print(f"\n💡 To change the model, edit the .env file or set MODEL_NAME environment variable")

if __name__ == "__main__":
    main() 