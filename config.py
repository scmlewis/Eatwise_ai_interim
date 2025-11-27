"""
EatWise AI - Ultra-Minimal Configuration
Only essential settings for LLM-powered interim version
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ===========================
# App Configuration
# ===========================

APP_NAME = "EatWise AI"
APP_VERSION = "1.0.0-interim"

# ===========================
# Azure OpenAI Configuration (HKUST - works in Hong Kong)
# ===========================

OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hkust.azure-api.net/")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# Validate API key is set
if not OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set. Please add it to your .env file")
