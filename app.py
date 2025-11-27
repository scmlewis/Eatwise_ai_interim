"""
EatWise AI - Ultra-Minimal Interim Version
Pure LLM-focused food intelligence without database or authentication
Session-only profile: user data resets on page refresh
"""

import streamlit as st
from datetime import datetime
from PIL import Image
import io
import re
from nutrition_analyzer import NutritionAnalyzer
from config import APP_NAME, OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION

# ===========================
# API Configuration (Override with Streamlit secrets if available)
# ===========================

api_key = OPENAI_API_KEY
endpoint = AZURE_OPENAI_ENDPOINT
deployment = AZURE_OPENAI_DEPLOYMENT
api_version = AZURE_OPENAI_API_VERSION

# Try to load from Streamlit secrets (for Streamlit Cloud)
try:
    api_key = st.secrets.get("AZURE_OPENAI_API_KEY") or api_key
    endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT") or endpoint
    deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT") or deployment
    api_version = st.secrets.get("AZURE_OPENAI_API_VERSION") or api_version
except (AttributeError, FileNotFoundError):
    # st.secrets not available, use config values
    pass

# ===========================
# API Key Validation
# ===========================

if not api_key:
    st.error("""
    ❌ **Missing Azure OpenAI API Key**
    
    Please configure your Streamlit secrets or .env file with:
    
    ```
    AZURE_OPENAI_API_KEY=your_api_key_here
    AZURE_OPENAI_ENDPOINT=https://hkust.azure-api.net/
    AZURE_OPENAI_DEPLOYMENT=gpt-4o
    AZURE_OPENAI_API_VERSION=2023-05-15
    ```
    
    See `docs/setup/.env.example` for a template.
    """)
    st.stop()

# Debug logging (remove after troubleshooting)
import sys
print(f"DEBUG APP: API Key set: {bool(api_key)}", file=sys.stderr)
print(f"DEBUG APP: Endpoint: {endpoint}", file=sys.stderr)
print(f"DEBUG APP: API Version: {api_version}", file=sys.stderr)
print(f"DEBUG APP: Deployment: {deployment}", file=sys.stderr)

# ===========================
# Page Configuration
# ===========================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================
# Session State Initialization
# ===========================

def init_session_state():
    """Initialize session state with user profile"""
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "age_group": "Not selected",
            "health_conditions": [],
            "dietary_preferences": [],
            "health_goal": "General wellness"
        }
    
    if "current_analysis" not in st.session_state:
        st.session_state.current_analysis = None

init_session_state()

# ===========================
# Analysis Display Helper with Advanced Styling
# ===========================

def extract_nutrition_numbers(text: str) -> dict:
    """Extract nutrition information from the analysis text"""
    nutrition = {}
    
    # More flexible pattern matching for nutrition data
    patterns = {
        'calories': [
            r'\*\*calories?\*\*:?\s*(\d+)',
            r'calories?:?\s*(\d+)(?:\s*-\s*|\s*to\s*)(\d+)',
            r'(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*calories',
            r'approximately?\s*(\d+)\s*calories',
            r'about\s*(\d+)\s*kcal',
            r'(\d+)\s*(?:calories?|kcal|cal(?:ories)?)'
        ],
        'protein': [
            r'\*\*protein\*\*:?\s*(\d+)\s*g',
            r'protein:?\s*(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g',
            r'(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g(?:ram)?s?(?:\s*of)?\s*protein',
            r'(\d+)\s*(?:gram)?s?(?:\s*of)?\s*protein',
            r'protein:?\s*(\d+)\s*g'
        ],
        'carbs': [
            r'\*\*carbs?(?:ohydrate)?s?\*\*:?\s*(\d+)\s*g',
            r'carbs?(?:ohydrate)?s?:?\s*(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g',
            r'(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g(?:ram)?s?(?:\s*of)?\s*carbs?(?:ohydrate)?s?',
            r'(\d+)\s*g(?:ram)?s?(?:\s*of)?\s*carbs?(?:ohydrate)?s?',
            r'carbs?(?:ohydrate)?s?:?\s*(\d+)\s*g'
        ],
        'fat': [
            r'\*\*fat\*\*:?\s*(\d+)\s*g',
            r'fat:?\s*(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g',
            r'(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g(?:ram)?s?(?:\s*of)?\s*fat',
            r'(\d+)\s*g(?:gram)?s?(?:\s*of)?\s*fat',
            r'fat:?\s*(\d+)\s*g'
        ],
        'fiber': [
            r'\*\*fiber\*\*:?\s*(\d+)\s*g',
            r'fiber:?\s*(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g',
            r'(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g(?:ram)?s?(?:\s*of)?\s*fiber',
            r'(\d+)\s*g(?:ram)?s?(?:\s*of)?\s*fiber',
            r'fiber:?\s*(\d+)\s*g'
        ],
        'sodium': [
            r'\*\*sodium\*\*:?\s*(\d+)\s*mg',
            r'sodium:?\s*(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*mg',
            r'(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*mg(?:\s*of)?\s*sodium',
            r'(\d+)\s*mg(?:\s*of)?\s*sodium',
            r'sodium:?\s*(\d+)\s*mg'
        ],
        'sugar': [
            r'\*\*sugar\*\*:?\s*(\d+)\s*g',
            r'sugar:?\s*(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g',
            r'(\d+)(?:\s*-\s*|\s*to\s*)(\d+)\s*g(?:ram)?s?(?:\s*of)?\s*sugar',
            r'(\d+)\s*g(?:ram)?s?(?:\s*of)?\s*sugar',
            r'sugar:?\s*(\d+)\s*g'
        ]
    }
    
    text_lower = text.lower()
    
    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # Get the matched text
                raw_value = match.group(0).strip()
                
                # Extract just the numbers and units
                numbers = re.findall(r'\d+', raw_value)
                if numbers:
                    # For ranges, show "X-Y" format; for single values, just show the number
                    if len(numbers) >= 2 and 'to' in raw_value.lower() or '-' in raw_value:
                        value = f"{numbers[0]}-{numbers[1]}"
                    else:
                        value = numbers[0] if numbers else raw_value
                    
                    # Add unit
                    if key == 'calories':
                        nutrition[key] = f"{value} cal"
                    elif key == 'sodium':
                        nutrition[key] = f"{value} mg"
                    else:
                        nutrition[key] = f"{value} g"
                    break  # Found match for this nutrient, move to next
    
    return nutrition

def extract_rating(text: str) -> tuple:
    """Extract health rating score and max score"""
    # Look for patterns like "Health Rating: 7/10", "7/10", "7 out of 10"
    patterns = [
        r'\*\*health\s+rating\*\*:?\s*(\d+)\s*(?:/|out\s*of)\s*(\d+)',
        r'health\s+rating\s*:\s*(\d+)\s*(?:/|out\s*of)\s*(\d+)',
        r'rating\s*:\s*(\d+)\s*(?:/|out\s*of)\s*(\d+)',
        r'(\d+)\s*(?:/|out\s*of)\s*(\d+)\s*(?:for\s+health|health\s+rating)',
        r'(?:health\s+)?(?:rating[:\s]+)?(\d+)\s*(?:/|out\s*of)\s*(\d+)',
    ]
    
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                score = int(match.group(1))
                max_score = int(match.group(2))
                if 0 < score <= max_score:  # Score must be positive
                    return score, max_score
            except (ValueError, IndexError):
                continue
    
    return None, None

def display_meal_analysis(analysis_text: str):
    """Display meal analysis with beautiful, well-organized sections"""
    
    # Custom CSS for better styling with proper contrast
    st.markdown("""
    <style>
    .meal-analysis-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-header {
        font-size: 1.3em;
        font-weight: 600;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        color: #00d4ff;
        border-bottom: 3px solid #00d4ff;
        padding-bottom: 0.5em;
    }
    .nutrition-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2em;
        border-radius: 12px;
        color: white;
        margin: 0.5em 0;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .nutrition-card-value {
        font-size: 1.15em;
        color: #ffffff;
        font-weight: 600;
    }
    .app-header {
        background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%);
        padding: 2em;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1em;
        box-shadow: 0 8px 25px rgba(20, 184, 166, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    .app-title {
        font-size: 3.5em;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 2px;
        margin: 0;
    }
    .app-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1em;
        margin-top: 0.5em;
        font-weight: 300;
    }
    .app-intro {
        background: rgba(100, 150, 255, 0.1);
        border-left: 5px solid #6366f1;
        padding: 1.5em;
        border-radius: 10px;
        margin-bottom: 2em;
        color: #ffffff;
        line-height: 1.8;
    }
    .intro-features {
        margin-top: 1em;
        padding-top: 1em;
        border-top: 1px solid rgba(99, 102, 241, 0.3);
    }
    .intro-features li {
        margin: 0.5em 0;
    }
    .rating-score {
        font-size: 3em;
        font-weight: bold;
        color: #00d4ff;
        text-align: center;
        margin: 0.5em 0;
    }
    .rating-interpretation {
        text-align: center;
        font-weight: 600;
        font-size: 1.1em;
        margin-top: 0.8em;
    }
    .advice-item {
        background: rgba(100, 200, 255, 0.15);
        padding: 1.2em;
        border-left: 5px solid #00d4ff;
        margin: 1em 0;
        border-radius: 8px;
        line-height: 1.7;
        color: #ffffff;
        border-radius: 8px;
    }
    .food-item {
        background: rgba(255, 200, 100, 0.15);
        padding: 1.2em;
        border-left: 5px solid #ff8c42;
        margin: 0.8em 0;
        border-radius: 8px;
        font-size: 0.98em;
        color: #ffffff;
        line-height: 1.6;
    }
    .progress-bar {
        height: 8px;
        background: #1a3a52;
        border-radius: 10px;
        overflow: hidden;
        margin: 1em 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Split analysis into sentences for better parsing
    sentences = [s.strip() for s in analysis_text.split('.') if s.strip()]
    
    # Initialize containers
    food_description = ""
    nutrition_data = {}
    rating_score = None
    max_rating = None
    advice_list = []
    
    # Parse the analysis - collect all info
    full_text = analysis_text.lower()
    
    # Extract food description (usually first sentence)
    if sentences:
        food_description = sentences[0]
    
    # Extract nutrition data - search entire text
    nutrition_data = extract_nutrition_numbers(analysis_text)
    
    # Extract rating
    for sentence in sentences:
        score, max_s = extract_rating(sentence)
        if score:
            rating_score = score
            max_rating = max_s
            break
    
    # Extract advice - sentences with recommendation keywords
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(word in sentence_lower for word in ['consider', 'recommend', 'suggest', 'try', 'opt for', 'balance', 'incorporate', 'avoid', 'reduce', 'increase', 'prefer']):
            if len(sentence) > 15:  # Filter out very short sentences
                advice_list.append(sentence)
    
    # DISPLAY SECTION 1: Food Items (Top Left)
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown('<div class="section-header">🍽️ Detected Food Items</div>', unsafe_allow_html=True)
        if food_description:
            st.markdown(f'<div class="food-item">{food_description}</div>', unsafe_allow_html=True)
        else:
            st.info("Food identification in progress...")
    
    with col2:
        st.markdown('<div class="section-header">💪 Health Rating</div>', unsafe_allow_html=True)
        if rating_score and max_rating:
            st.markdown(f'<div class="rating-score">{rating_score}/{max_rating}</div>', unsafe_allow_html=True)
            
            # Custom progress bar
            progress_pct = (rating_score / max_rating) * 100
            st.markdown(f'''
            <div class="progress-bar">
                <div style="width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 10px;"></div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Add rating interpretation
            if rating_score >= 8:
                rating_text = "Excellent choice! 🌟"
                color = "#2ecc71"
            elif rating_score >= 6:
                rating_text = "Good balance 👍"
                color = "#f39c12"
            else:
                rating_text = "Consider improvements 💡"
                color = "#ff6b6b"
            
            st.markdown(f'<p class="rating-interpretation" style="color: {color};">{rating_text}</p>', unsafe_allow_html=True)
        else:
            st.info("Rating information will appear here")
    
    st.divider()
    
    # DISPLAY SECTION 2: Nutrition Breakdown (Full Width)
    st.markdown('<div class="section-header">📊 Nutrition Breakdown</div>', unsafe_allow_html=True)
    
    if nutrition_data:
        # Create a grid for nutrition data
        nutrition_cols = st.columns(len(nutrition_data) if nutrition_data else 1)
        
        nutrition_icons = {
            'calories': '🔥',
            'protein': '💪',
            'carbs': '🌾',
            'fat': '🥑',
            'fiber': '🥗',
            'sodium': '🧂',
            'sugar': '🍬'
        }
        
        col_idx = 0
        for key, value in nutrition_data.items():
            if col_idx >= len(nutrition_cols):
                break
            
            icon = nutrition_icons.get(key, '📌')
            with nutrition_cols[col_idx]:
                st.markdown(
                    f'''<div class="nutrition-card">
                        <div style="font-size: 1.3em; margin-bottom: 0.5em;">{icon} {key.capitalize()}</div>
                        <div class="nutrition-card-value">{value}</div>
                    </div>''',
                    unsafe_allow_html=True
                )
            col_idx += 1
    else:
        st.info("📊 Nutritional details being extracted...")
    
    st.divider()
    
    # DISPLAY SECTION 3: Personalized Advice (Full Width)
    st.markdown('<div class="section-header">💡 Personalized Advice</div>', unsafe_allow_html=True)
    
    if advice_list:
        # Combine all advice into a single paragraph and strip markdown
        combined_advice = " ".join(advice_list)
        # Remove markdown formatting (**, *, etc.)
        combined_advice = re.sub(r'\*\*(.+?)\*\*', r'\1', combined_advice)  # Remove bold
        combined_advice = re.sub(r'\*(.+?)\*', r'\1', combined_advice)  # Remove italics
        combined_advice = re.sub(r'_(.+?)_', r'\1', combined_advice)  # Remove underscores
        st.markdown(f'<div class="advice-item">✨ {combined_advice}</div>', unsafe_allow_html=True)
    else:
        # Fallback: show informational message
        st.info("💡 Personalized recommendations will appear here based on your profile and the meal analysis...")

init_session_state()

# ===========================
# Global CSS Styling
# ===========================

st.markdown("""
<style>
/* Main App Header */
.app-header {
    background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%);
    padding: 1.8em 2em;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 1em;
    box-shadow: 0 12px 30px rgba(20, 184, 166, 0.35);
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.app-title {
    font-size: 3.2em;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 2px;
    margin: 0;
}

.app-subtitle {
    color: rgba(255, 255, 255, 0.95);
    font-size: 1em;
    margin-top: 0.4em;
    font-weight: 300;
}

/* Section Headers */
.section-header {
    font-size: 1.25em;
    font-weight: 700;
    margin-top: 1.2em;
    margin-bottom: 0.7em;
    color: #06b6d4;
    border-bottom: 3px solid #06b6d4;
    padding-bottom: 0.4em;
}

/* Nutrition Cards */
.nutrition-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1em 1.2em;
    border-radius: 12px;
    color: white;
    margin: 0.4em 0;
    font-weight: 600;
    text-align: center;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.nutrition-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 7px 20px rgba(102, 126, 234, 0.45);
}

.nutrition-card-value {
    font-size: 1.1em;
    color: #ffffff;
    font-weight: 700;
}

/* Rating Section */
.rating-score {
    font-size: 2.8em;
    font-weight: 900;
    color: #06b6d4;
    text-align: center;
    margin: 0.5em 0;
}

.rating-interpretation {
    text-align: center;
    font-weight: 700;
    font-size: 1em;
    margin-top: 0.6em;
}

/* Progress Bar */
.progress-bar {
    height: 8px;
    background: rgba(6, 182, 212, 0.15);
    border-radius: 10px;
    overflow: hidden;
    margin: 0.8em 0;
    border: 1px solid rgba(6, 182, 212, 0.3);
}

/* Advice Items */
.advice-item {
    background: rgba(6, 182, 212, 0.12);
    padding: 1em 1.2em;
    border-left: 5px solid #06b6d4;
    margin: 0.8em 0;
    border-radius: 8px;
    line-height: 1.6;
    color: #ffffff;
    box-shadow: 0 3px 12px rgba(6, 182, 212, 0.15);
}

/* Food Item */
.food-item {
    background: rgba(255, 140, 66, 0.12);
    padding: 1em 1.2em;
    border-left: 5px solid #ff8c42;
    margin: 0.6em 0;
    border-radius: 8px;
    font-size: 0.95em;
    color: #ffffff;
    line-height: 1.6;
    box-shadow: 0 3px 12px rgba(255, 140, 66, 0.12);
}

/* Meal Analysis Container */
.meal-analysis-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Tab styling adjustments */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5em;
}

.stTabs [data-baseweb="tab"] {
    padding: 0.7em 1.2em;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# ===========================
# Sidebar - User Profile (Session Only)
# ===========================

with st.sidebar:
    # About the App - Top Section with Sharp Styling
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%);
        border-radius: 12px;
        padding: 1.2em;
        margin-bottom: 1.5em;
        box-shadow: 0 4px 15px rgba(20, 184, 166, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    ">
        <div style="font-size: 1.2em; font-weight: 700; color: #ffffff; margin-bottom: 0.8em;">
            🚀 EatWise
        </div>
        <div style="
            color: rgba(255, 255, 255, 0.95);
            font-size: 0.9em;
            line-height: 1.6;
        ">
            <p style="margin: 0.4em 0; color: rgba(255, 255, 255, 0.9);">
                <strong>AI Nutrition Assistant</strong>
            </p>
            <ul style="margin: 0.6em 0; padding-left: 1.2em; color: rgba(255, 255, 255, 0.85);">
                <li style="margin: 0.3em 0;">📸 Food photo detection</li>
                <li style="margin: 0.3em 0;">📊 Nutrition analysis</li>
                <li style="margin: 0.3em 0;">💡 Personalized coaching</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 👤 Your Profile")
    
    st.session_state.profile["age_group"] = st.selectbox(
        "Age Group",
        ["Not selected", "18-25", "26-35", "36-45", "46-55", "56+"],
        index=0 if st.session_state.profile["age_group"] == "Not selected" else 
              ["Not selected", "18-25", "26-35", "36-45", "46-55", "56+"].index(st.session_state.profile["age_group"])
    )
    
    st.session_state.profile["health_conditions"] = st.multiselect(
        "Health Conditions",
        ["Diabetes", "Hypertension", "Heart Disease", "Celiac", "Lactose Intolerance"],
        default=st.session_state.profile["health_conditions"]
    )
    
    st.session_state.profile["dietary_preferences"] = st.multiselect(
        "Dietary Preferences",
        ["Vegetarian", "Vegan", "Gluten-Free", "Low-Carb", "Keto"],
        default=st.session_state.profile["dietary_preferences"]
    )
    
    st.session_state.profile["health_goal"] = st.selectbox(
        "Health Goal",
        ["General wellness", "Weight loss", "Muscle gain", "Better energy", "Disease management"],
        index=["General wellness", "Weight loss", "Muscle gain", "Better energy", "Disease management"].index(st.session_state.profile["health_goal"])
    )

# ===========================
# Main Content - App Header
# ===========================

st.markdown('''
<div class="app-header">
    <div class="app-title">🍽️ EatWise</div>
    <div class="app-subtitle">Intelligent Meal Analysis & Personalized Nutrition Coaching</div>
</div>
''', unsafe_allow_html=True)

# ===========================
# Main Content - Tabs
# ===========================

tab1, tab2 = st.tabs(["🍽️ Meal Analysis", "💡 Coaching Tips"])

# ===========================
# Tab 1: Meal Analysis (Combined Food Detection + Nutrition)
# ===========================

with tab1:
    st.markdown("## 🍽️ Meal Analysis")
    st.markdown("Analyze your meal by **photo** or by **description**. Get instant nutrition insights and personalized recommendations.")
    
    # Choose analysis method
    analysis_method = st.radio(
        "How would you like to analyze your meal?",
        ["📝 Describe Your Meal", "📸 Upload Food Photo"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if analysis_method == "📸 Upload Food Photo":
        st.markdown("### 📸 Upload a Food Photo")
        uploaded_file = st.file_uploader(
            "Choose a food image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # Display the uploaded image
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📷 Your Photo")
                image = Image.open(uploaded_file)
                st.image(image, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 Ready to Analyze")
                st.write("Click the button below to analyze your meal")
            
            if st.button("🔍 Analyze Meal", use_container_width=True, type="primary"):
                with st.spinner("🔍 Analyzing your meal photo..."):
                    analyzer = NutritionAnalyzer(
                        api_key,
                        endpoint,
                        deployment,
                        api_version
                    )
                    
                    # Convert image to bytes
                    image_bytes = io.BytesIO()
                    image.save(image_bytes, format="PNG")
                    image_bytes.seek(0)
                    image_base64 = io.BytesIO(uploaded_file.getvalue()).read()
                    
                    try:
                        analysis = analyzer.detect_food_from_image(
                            image_base64,
                            st.session_state.profile
                        )
                        
                        st.session_state.current_analysis = analysis
                        
                        # Show success notification
                        st.success("✅ Analysis complete!", icon="✅")
                        
                        display_meal_analysis(analysis)
                            
                    except Exception as e:
                        st.error(f"❌ Error analyzing image: {str(e)}")
                        st.info("Make sure your Azure OpenAI API key is correct in .env file")
                    st.info("Make sure your Azure OpenAI API key is correct in .env file")
    
    else:  # Describe Meal
        st.markdown("### 📝 Describe Your Meal")
        meal_description = st.text_area(
            "Describe your meal in detail",
            placeholder="e.g., A grilled chicken breast with steamed broccoli and brown rice, seasoned with olive oil and garlic. Plus a glass of orange juice.",
            height=120,
            label_visibility="collapsed"
        )
        
        if st.button("🔍 Analyze Meal", use_container_width=True, type="primary"):
            if meal_description.strip():
                with st.spinner("📊 Analyzing your meal..."):
                    analyzer = NutritionAnalyzer(
                        api_key,
                        endpoint,
                        deployment,
                        api_version
                    )
                    
                    try:
                        analysis = analyzer.analyze_text_meal(
                            meal_description,
                            st.session_state.profile
                        )
                        
                        st.session_state.current_analysis = analysis
                        
                        # Show success notification
                        st.success("✅ Analysis complete!", icon="✅")
                        
                        display_meal_analysis(analysis)
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing meal: {str(e)}")
                        st.info("Make sure your Azure OpenAI API key is correct in .env file")
            else:
                st.warning("Please describe your meal first!")

# ===========================
# Tab 2: Personalized Coaching
# ===========================

with tab2:
    st.markdown("## 💡 Personalized Nutrition Coaching")
    st.markdown("Get personalized tips and recommendations based on your profile and goals.")
    
    coaching_topic = st.selectbox(
        "What would you like coaching on?",
        [
            "Daily nutrition tips",
            "How to improve my diet for my health goal",
            "Healthy meal ideas based on my preferences",
            "Energy and metabolism optimization",
            "Managing meals with my health conditions",
            "Hydration and supplements advice"
        ]
    )
    
    if st.button("💡 Get Coaching Tips", use_container_width=True, type="primary"):
        with st.spinner("✨ Generating personalized tips..."):
            analyzer = NutritionAnalyzer(
                api_key,
                endpoint,
                deployment,
                api_version
            )
            
            try:
                coaching = analyzer.get_personalized_coaching(
                    coaching_topic,
                    st.session_state.profile
                )
                
                st.session_state.current_analysis = coaching
                
                # Show success notification
                st.success("✅ Coaching tips ready!", icon="✅")
                
                st.markdown("### Your Personalized Tips")
                st.markdown(f'<div class="advice-item">💡 {coaching}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error generating coaching: {str(e)}")
                st.info("Make sure your Azure OpenAI API key is correct in .env file")

# ===========================
# Footer
# ===========================

st.markdown("""
<div style="text-align: center; color: rgba(255, 255, 255, 0.6); font-size: 0.9em; padding: 1.5em 0;">
    <p>✨ <strong>Built with</strong> Streamlit + Azure OpenAI GPT-4 Vision</p>
</div>
""", unsafe_allow_html=True)
