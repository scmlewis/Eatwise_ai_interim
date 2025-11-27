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
# Note: These will be overridden by Streamlit secrets if available
# ===========================

OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hkust.azure-api.net/")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")


def get_config_from_secrets():
    """Get configuration from Streamlit secrets (for Streamlit Cloud)"""
    try:
        import streamlit as st
        api_key = st.secrets.get("AZURE_OPENAI_API_KEY")
        endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", "https://hkust.azure-api.net/")
        deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        api_version = st.secrets.get("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
        
        return api_key, endpoint, deployment, api_version
    except:
        return None, None, None, None
