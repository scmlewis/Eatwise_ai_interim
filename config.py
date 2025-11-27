"""
EatWise AI - Ultra-Minimal Configuration
Only essential settings for LLM-powered interim version
"""

import os
import streamlit as st
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

# Try to get from Streamlit secrets first (for Streamlit Cloud), then from .env (for local dev)
try:
    OPENAI_API_KEY = st.secrets.get("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = st.secrets.get("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT", "https://hkust.azure-api.net/")
    AZURE_OPENAI_DEPLOYMENT = st.secrets.get("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
except:
    # If st.secrets is not available (not in Streamlit context), use env vars
    OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hkust.azure-api.net/")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# Note: API key validation moved to app.py for better error messaging
