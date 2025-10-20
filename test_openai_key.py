"""Test if OpenAI API key is properly configured"""
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Check OpenAI key
openai_key = os.getenv("OPENAI_API_KEY")

if openai_key and openai_key != "your_openai_key_here":
    print("[OK] OpenAI API key is configured!")
    print(f"Key starts with: {openai_key[:15]}...")

    # Try to import and initialize OpenAI
    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        print("[OK] OpenAI client initialized successfully!")
        print("\nReady to generate graphics!")
    except Exception as e:
        print(f"[ERROR] Error initializing OpenAI: {e}")
else:
    print("[ERROR] OpenAI API key not found or not configured")
    print(f"Current value: {openai_key}")
