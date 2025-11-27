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
# Try Streamlit secrets first, then fall back to environment variables
# ===========================

# Try to load from Streamlit secrets if available
try:
    OPENAI_API_KEY = st.secrets["AZURE_OPENAI_API_KEY"]
    AZURE_OPENAI_ENDPOINT = st.secrets.get("AZURE_OPENAI_ENDPOINT", "https://hkust.azure-api.net/")
    AZURE_OPENAI_DEPLOYMENT = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    AZURE_OPENAI_API_VERSION = st.secrets.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
except (KeyError, AttributeError, FileNotFoundError):
    # Fall back to environment variables for local development
    OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hkust.azure-api.net/")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
