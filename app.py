"""
EatWise AI - Interim Version
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

# Add anchor for back-to-top functionality
st.markdown('<a id="app-top"></a>', unsafe_allow_html=True)

# Add floating back-to-top button (experimental)
st.markdown("""
<style>
.floating-back-to-top {
    position: fixed;
    bottom: 100px;
    right: 25px;
    z-index: 999;
}

.floating-back-to-top a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%);
    color: white;
    border-radius: 50%;
    text-decoration: none;
    font-size: 1.8em;
    box-shadow: 0 6px 20px rgba(20, 184, 166, 0.5);
    transition: all 0.3s ease;
    border: 2px solid rgba(255, 255, 255, 0.3);
    line-height: 1;
    font-weight: bold;
}

.floating-back-to-top a:hover {
    transform: translateY(-8px) scale(1.1);
    box-shadow: 0 10px 30px rgba(20, 184, 166, 0.7);
    border-color: rgba(255, 255, 255, 0.5);
}

.floating-back-to-top a:active {
    transform: translateY(-4px) scale(1.05);
}
</style>

<div class="floating-back-to-top">
    <a href="#app-top" title="Back to top">↑</a>
</div>
""", unsafe_allow_html=True)

# ===========================
# Session State Initialization
# ===========================

def init_session_state():
    """Initialize session state with user profile"""
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "age_group": "Not selected",
            "gender": "Not selected",
            "health_conditions": [],
            "dietary_preferences": [],
            "health_goal": "General wellness"
        }
    else:
        # Ensure gender field exists for backward compatibility
        if "gender" not in st.session_state.profile:
            st.session_state.profile["gender"] = "Not selected"
    
    if "current_analysis" not in st.session_state:
        st.session_state.current_analysis = None
    
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    
    if "analysis_method" not in st.session_state:
        st.session_state.analysis_method = "text"

init_session_state()

# ===========================
# Nutrition Targets Helper
# ===========================

def get_nutrition_targets(profile: dict) -> dict:
    """Calculate personalized nutrition targets based on profile (gender + health goal)"""
    health_goal = profile.get("health_goal", "General wellness")
    gender = profile.get("gender", "Not selected")
    
    # Base targets by health goal
    base_targets = {
        "General wellness": {"calories": 2000, "protein": 50, "carbs": 225, "fat": 65, "fiber": 25, "sodium": 2300},
        "Weight loss": {"calories": 1500, "protein": 120, "carbs": 150, "fat": 50, "fiber": 30, "sodium": 2000},
        "Muscle gain": {"calories": 2500, "protein": 150, "carbs": 300, "fat": 85, "fiber": 25, "sodium": 2300},
        "Energy boost": {"calories": 2200, "protein": 70, "carbs": 275, "fat": 70, "fiber": 28, "sodium": 2300},
        "Heart health": {"calories": 1800, "protein": 60, "carbs": 200, "fat": 50, "fiber": 35, "sodium": 1500},
    }
    
    targets = base_targets.get(health_goal, base_targets["General wellness"])
    
    # Adjust for gender (standard nutritional guidelines)
    if gender == "Female":
        # Women typically need 10-15% fewer calories
        targets["calories"] = int(targets["calories"] * 0.85)
        # Protein adjusted proportionally (0.8g per lb bodyweight for women)
        targets["protein"] = int(targets["protein"] * 0.85)
    elif gender == "Male":
        # Men typically need 10-15% more calories
        targets["calories"] = int(targets["calories"] * 1.1)
        # Protein adjusted proportionally
        targets["protein"] = int(targets["protein"] * 1.1)
    
    return targets

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

def generate_quick_tips(nutrition_data: dict, profile: dict) -> list:
    """Generate contextual quick tips based on detected nutrients vs targets"""
    tips = []
    
    # Get targets for the user's health goal
    targets = get_nutrition_targets(profile)
    
    # Extract numeric values from nutrition data
    def get_numeric_value(value_str):
        """Extract numeric value from strings like '450 cal' or '25 g'"""
        if not value_str:
            return 0
        import re
        match = re.search(r'(\d+)', str(value_str))
        return int(match.group(1)) if match else 0
    
    # Check protein intake
    protein_val = get_numeric_value(nutrition_data.get('protein', '0'))
    protein_target = targets.get('protein', 50)
    if protein_val >= protein_target * 0.9:
        tips.append("💪 Excellent protein intake!")
    elif protein_val < protein_target * 0.3:
        tips.append("💪 Consider adding more protein-rich foods")
    
    # Check fiber intake
    fiber_val = get_numeric_value(nutrition_data.get('fiber', '0'))
    fiber_target = targets.get('fiber', 25)
    if fiber_val >= fiber_target * 0.8:
        tips.append("🥗 Great fiber content!")
    elif fiber_val < fiber_target * 0.3:
        tips.append("🥗 Add more fiber with whole grains and vegetables")
    
    # Check sodium intake
    sodium_val = get_numeric_value(nutrition_data.get('sodium', '0'))
    sodium_target = targets.get('sodium', 2300)
    if sodium_val > sodium_target * 0.8:
        tips.append("🧂 Watch the sodium intake in this meal")
    
    # Check calorie balance
    calories_val = get_numeric_value(nutrition_data.get('calories', '0'))
    calories_target = targets.get('calories', 2000)
    if calories_val > calories_target * 1.2:
        tips.append("🔥 This meal is calorie-dense for the daily target")
    elif calories_val < calories_target * 0.3 and calories_val > 50:
        tips.append("🔥 Light meal - consider pairing with other foods")
    
    # Check carbs
    carbs_val = get_numeric_value(nutrition_data.get('carbs', '0'))
    protein_ratio = (protein_val / (carbs_val + 1)) * 100
    if protein_ratio > 50:
        tips.append("⚡ High protein-to-carb ratio - good balance")
    
    # Add a positive note if everything looks good
    if not tips:
        tips.append("✅ Balanced meal composition")
    
    return tips[:3]  # Return top 3 tips

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
        st.markdown('<div class="section-header">🍽️ Your Meal</div>', unsafe_allow_html=True)
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
        nutrition_icons = {
            'calories': '🔥',
            'protein': '💪',
            'carbs': '🌾',
            'fat': '🥑',
            'fiber': '🥗',
            'sodium': '🧂',
            'sugar': '🍬'
        }
        
        # Create a responsive grid layout (3 columns)
        nutrition_items = list(nutrition_data.items())
        cols_per_row = 3
        
        for row_idx in range(0, len(nutrition_items), cols_per_row):
            cols = st.columns(cols_per_row, gap="small")
            row_items = nutrition_items[row_idx:row_idx + cols_per_row]
            
            for col_idx, (key, value) in enumerate(row_items):
                icon = nutrition_icons.get(key, '📌')
                with cols[col_idx]:
                    st.markdown(
                        f'''<div class="nutrition-card">
                            <div style="font-size: 1.3em; margin-bottom: 0.5em;">{icon} {key.capitalize()}</div>
                            <div class="nutrition-card-value">{value}</div>
                        </div>''',
                        unsafe_allow_html=True
                    )
    else:
        st.info("📊 Nutritional details being extracted...")
    
    st.divider()
    
    # DISPLAY SECTION 2.5: Quick Tips
    if nutrition_data and "age_group" in st.session_state.profile and st.session_state.profile.get("age_group") != "Not selected":
        quick_tips = generate_quick_tips(nutrition_data, st.session_state.profile)
        if quick_tips:
            st.markdown('<div class="section-header">⚡ Quick Tips</div>', unsafe_allow_html=True)
            for tip in quick_tips:
                st.markdown(f'<div class="advice-item">{tip}</div>', unsafe_allow_html=True)
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
    st.info("**Required fields** (marked with ✓) are needed for personalized nutrition targets and coaching tips. Others are optional.")
    
    st.session_state.profile["age_group"] = st.selectbox(
        "Age Group ✓ **(Required)**",
        ["Not selected", "18-25", "26-35", "36-45", "46-55", "56+"],
        index=0 if st.session_state.profile["age_group"] == "Not selected" else 
              ["Not selected", "18-25", "26-35", "36-45", "46-55", "56+"].index(st.session_state.profile["age_group"])
    )
    
    st.session_state.profile["gender"] = st.selectbox(
        "Gender ✓ **(Required)**",
        ["Not selected", "Male", "Female", "Other"],
        index=0 if st.session_state.profile.get("gender", "Not selected") == "Not selected" else 
              ["Not selected", "Male", "Female", "Other"].index(st.session_state.profile.get("gender", "Not selected"))
    )
    
    st.session_state.profile["health_goal"] = st.selectbox(
        "Health Goal ✓ **(Required)**",
        ["General wellness", "Weight loss", "Muscle gain", "Energy boost", "Heart health"],
        index=["General wellness", "Weight loss", "Muscle gain", "Energy boost", "Heart health"].index(st.session_state.profile["health_goal"])
    )
    
    st.session_state.profile["health_conditions"] = st.multiselect(
        "Health Conditions (Optional)",
        ["Diabetes", "Hypertension", "Heart Disease", "Celiac", "Lactose Intolerance"],
        default=st.session_state.profile["health_conditions"]
    )
    
    st.session_state.profile["dietary_preferences"] = st.multiselect(
        "Dietary Preferences (Optional)",
        ["Vegetarian", "Vegan", "Gluten-Free", "Low-Carb", "Keto"],
        default=st.session_state.profile["dietary_preferences"]
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

tab1, tab2, tab3 = st.tabs(["🍽️ Meal Analysis", "🎯 Nutrition Targets", "💡 Coaching Tips"])

# ===========================
# Tab 1: Meal Analysis (Combined Food Detection + Nutrition)
# ===========================

with tab1:
    st.markdown("## 🍽️ Meal Analysis")
    st.markdown("Analyze your meal by **photo** or by **description**. Get instant nutrition insights and personalized recommendations.")
    
    # Segmented button group for analysis method
    btn_col1, btn_col2 = st.columns(2, gap="small")
    
    with btn_col1:
        if st.button(
            "📝 Describe Your Meal",
            use_container_width=True,
            type="primary" if st.session_state.analysis_method == "text" else "secondary",
            key="btn_describe"
        ):
            st.session_state.analysis_method = "text"
            st.rerun()
    
    with btn_col2:
        if st.button(
            "📸 Upload Food Photo",
            use_container_width=True,
            type="primary" if st.session_state.analysis_method == "image" else "secondary",
            key="btn_upload"
        ):
            st.session_state.analysis_method = "image"
            st.rerun()
    
    st.markdown("")  # Spacing
    
    if st.session_state.analysis_method == "image":
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
            
            col_analyze, col_clear = st.columns(2, gap="small")
            
            with col_analyze:
                analyze_clicked = st.button("🔍 Analyze Meal", use_container_width=True, type="primary")
            
            with col_clear:
                clear_clicked = st.button("🗑️ Clear", use_container_width=True)
            
            if analyze_clicked:
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
                        
                        # Add to history (keep last 5)
                        from datetime import datetime
                        rating_score, rating_max = extract_rating(analysis)
                        # Extract food from analysis (first sentence usually contains food name)
                        food_name = analysis.split('.')[0] if '.' in analysis else analysis[:100]
                        history_entry = {
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "food": food_name[:100],
                            "rating": f"{rating_score}/{rating_max}" if rating_score else "N/A",
                            "analysis": analysis
                        }
                        st.session_state.analysis_history.insert(0, history_entry)
                        if len(st.session_state.analysis_history) > 5:
                            st.session_state.analysis_history = st.session_state.analysis_history[:5]
                            
                    except Exception as e:
                        st.error(f"❌ Error analyzing image: {str(e)}")
                        st.info("Make sure your Azure OpenAI API key is correct in .env file")
    
    elif st.session_state.analysis_method == "text":  # Describe Meal
        st.markdown("### 📝 Describe Your Meal")
        meal_description = st.text_area(
            "Describe your meal in detail",
            placeholder="e.g., A grilled chicken breast with steamed broccoli and brown rice, seasoned with olive oil and garlic. Plus a glass of orange juice.",
            height=120,
            label_visibility="collapsed"
        )
        
        col_analyze, col_clear = st.columns(2, gap="small")
        
        with col_analyze:
            analyze_clicked = st.button("🔍 Analyze Meal", use_container_width=True, type="primary", key="btn_analyze_text")
        
        with col_clear:
            clear_clicked = st.button("🗑️ Clear", use_container_width=True, key="btn_clear_text")
        
        if analyze_clicked:
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
                        
                        # Add to history (keep last 5)
                        from datetime import datetime
                        rating_score, rating_max = extract_rating(analysis)
                        history_entry = {
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "food": meal_description[:100],
                            "rating": f"{rating_score}/{rating_max}" if rating_score else "N/A",
                            "analysis": analysis
                        }
                        st.session_state.analysis_history.insert(0, history_entry)
                        if len(st.session_state.analysis_history) > 5:
                            st.session_state.analysis_history = st.session_state.analysis_history[:5]
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing meal: {str(e)}")
                        st.info("Make sure your Azure OpenAI API key is correct in .env file")
            else:
                st.warning("Please describe your meal first!")
        
        if clear_clicked:
            # Clear the meal description
            st.session_state.meal_description = ""
            st.rerun()

# ===========================
# Tab 2: Personalized Coaching
# ===========================

with tab2:
    st.markdown("## 🎯 Your Nutrition Targets")
    st.markdown("Personalized daily nutrition goals based on your profile.")
    
    # Check if required fields are filled
    if st.session_state.profile["age_group"] == "Not selected":
        st.warning("⚠️ **Age Group is required** to calculate your nutrition targets. Please select your age group in the sidebar profile section.")
        st.info("👉 Look for the '👤 Your Profile' section in the left sidebar")
    else:
        # Get targets based on profile
        targets = get_nutrition_targets(st.session_state.profile)
        
        st.success(f"✅ Targets calculated for: **{st.session_state.profile['age_group']}** | Gender: **{st.session_state.profile.get('gender', 'Not selected')}** | Goal: **{st.session_state.profile['health_goal']}**")
        
        # Display targets in a nice grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="nutrition-card">
                <div style="font-size: 1.3em; margin-bottom: 0.5em;">🔥 Calories</div>
                <div class="nutrition-card-value">{targets['calories']}</div>
                <div style="font-size: 0.8em; color: rgba(255,255,255,0.8); margin-top: 0.5em;">kcal/day</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="nutrition-card">
                <div style="font-size: 1.3em; margin-bottom: 0.5em;">💪 Protein</div>
                <div class="nutrition-card-value">{targets['protein']}</div>
                <div style="font-size: 0.8em; color: rgba(255,255,255,0.8); margin-top: 0.5em;">g/day</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="nutrition-card">
                <div style="font-size: 1.3em; margin-bottom: 0.5em;">🌾 Carbs</div>
                <div class="nutrition-card-value">{targets['carbs']}</div>
                <div style="font-size: 0.8em; color: rgba(255,255,255,0.8); margin-top: 0.5em;">g/day</div>
            </div>
            """, unsafe_allow_html=True)
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.markdown(f"""
            <div class="nutrition-card">
                <div style="font-size: 1.3em; margin-bottom: 0.5em;">🥑 Fat</div>
                <div class="nutrition-card-value">{targets['fat']}</div>
                <div style="font-size: 0.8em; color: rgba(255,255,255,0.8); margin-top: 0.5em;">g/day</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="nutrition-card">
                <div style="font-size: 1.3em; margin-bottom: 0.5em;">🥗 Fiber</div>
                <div class="nutrition-card-value">{targets['fiber']}</div>
                <div style="font-size: 0.8em; color: rgba(255,255,255,0.8); margin-top: 0.5em;">g/day</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="nutrition-card">
                <div style="font-size: 1.3em; margin-bottom: 0.5em;">🧂 Sodium</div>
                <div class="nutrition-card-value">{targets['sodium']}</div>
                <div style="font-size: 0.8em; color: rgba(255,255,255,0.8); margin-top: 0.5em;">mg/day</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 💡 Tips to Meet Your Targets")
        st.markdown(f"""
        - **Calories**: {targets['calories']} kcal daily based on your **{st.session_state.profile['health_goal']}** goal
        - **Protein**: {targets['protein']}g helps with muscle and recovery
        - **Carbs**: {targets['carbs']}g provides energy throughout your day
        - **Fat**: {targets['fat']}g supports hormone and brain health
        - **Fiber**: {targets['fiber']}g aids digestion and satiety
        - **Sodium**: Keep under {targets['sodium']}mg for heart health
        """)
        
        # Add expandable documentation about nutrition target criteria
        with st.expander("📚 **How Are These Targets Calculated?** (Click to Learn More)"):
            st.markdown("""
            ### Nutrition Target Calculation Methodology
            
            Your personalized nutrition targets are calculated based on scientifically-backed guidelines:
            
            #### 📊 **Base Targets by Health Goal**
            EatWise uses established nutritional guidelines adjusted for five distinct health goals:
            
            - **General Wellness**: Balanced nutrition for overall health (2000 cal/day baseline)
            - **Weight Loss**: Moderate calorie deficit with high protein to preserve muscle (1500 cal/day)
            - **Muscle Gain**: Calorie surplus with elevated protein for muscle building (2500 cal/day)
            - **Energy Boost**: Optimized carbs and calories for sustained energy (2200 cal/day)
            - **Heart Health**: Lower sodium and optimized fat ratios for cardiovascular wellness (1800 cal/day)
            
            #### ♀️♂️ **Gender Adjustments**
            Base targets are adjusted by gender to account for physiological differences:
            
            - **Female**: ~85% of base targets (average lower caloric needs and protein requirements)
            - **Male**: ~110% of base targets (average higher caloric needs and protein requirements)
            - **Other**: Base targets applied as-is
            
            *Source: Standard nutritional guidelines recognize biological differences in metabolic rate and body composition.*
            
            #### 🎯 **Key Macronutrient Guidelines**
            
            | Nutrient | Basis | Notes |
            |----------|-------|-------|
            | **Protein** | 0.8-1.1g per lb of bodyweight (adjusted by goal) | Supports muscle maintenance and growth |
            | **Carbohydrates** | 45-65% of total calories | Primary energy source |
            | **Fat** | 20-35% of total calories | Essential for hormone and brain function |
            | **Fiber** | 25-35g/day | Supports digestive health and satiety |
            | **Sodium** | <2300mg/day (1500mg for heart health) | Follows FDA/AHA guidelines |
            
            #### 📖 **Information Sources**
            
            These targets are based on guidelines from:
            - **USDA Dietary Guidelines for Americans** (2020-2025)
            - **Academy of Nutrition and Dietetics** (AND)
            - **American Heart Association** (AHA) cardiovascular recommendations
            - **WHO/FAO** protein and energy requirements
            - **Mayo Clinic** and **Harvard Health** nutritional science
            
            #### ⚠️ **Important Notes**
            
            - These are **general recommendations** and individual needs may vary
            - Factors like age, weight, height, activity level, and metabolism affect actual requirements
            - **Consult a registered dietitian** for personalized medical nutrition therapy
            - If you have health conditions, adjust targets under professional guidance
            - These targets should work alongside your meal analysis, not replace professional medical advice
            
            #### 🔄 **How Targets Are Used**
            
            Your nutrition targets help:
            1. Set daily goals for balanced eating
            2. Compare against your actual meal nutrition (see in Meal Analysis tab)
            3. Provide context for the Quick Tips feature
            4. Guide coaching recommendations tailored to your health goal
            """)
        
        if st.session_state.profile["health_conditions"]:
            st.markdown(f"**Your Health Conditions:** {', '.join(st.session_state.profile['health_conditions'])}")
            st.info("💡 Remember to consider your health conditions when planning meals. The coaching section has tips for managing meals with your conditions.")

with tab3:
    st.markdown("## 💡 Personalized Nutrition Coaching")
    st.markdown("Get personalized tips and recommendations based on your profile and goals.")
    
    # Check if required fields are filled
    if st.session_state.profile["age_group"] == "Not selected":
        st.warning("⚠️ **Age Group is required** to get personalized coaching tips. Please select your age group in the sidebar profile section.")
        st.info("👉 Look for the '👤 Your Profile' section in the left sidebar marked with ✓ **(Required)**")
    else:
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
# Analysis History Section
# ===========================

st.divider()
st.markdown('<div class="section-header">📋 Analysis History (Last 5)</div>', unsafe_allow_html=True)

if st.session_state.analysis_history:
    for idx, record in enumerate(st.session_state.analysis_history, 1):
        with st.expander(f"📌 {idx}. {record['food'][:40]}... ({record['timestamp']}) - Rating: {record['rating']}"):
            st.markdown(f"**Food Analyzed:** {record['food']}")
            st.markdown(f"**Health Rating:** {record['rating']}")
            st.markdown(f"**Full Analysis:**")
            st.markdown(record['analysis'])
else:
    st.info("🍽️ No analysis history yet. Start by analyzing a meal to see your past records here!")

# Always show back-to-top button
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <a href="#app-top">
        <button style="
            width: 100%;
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        " onmouseover="this.style.transform='scale(1.02)'; this.style.boxShadow='0 6px 20px rgba(102, 126, 234, 0.6)';"
           onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 15px rgba(102, 126, 234, 0.4)';">
            ⬆️ Back to Top
        </button>
    </a>
    """, unsafe_allow_html=True)

# ===========================
# Footer
# ===========================

st.markdown("""
<div style="text-align: center; color: rgba(255, 255, 255, 0.6); font-size: 0.9em; padding: 1.5em 0;">
    <p>✨ <strong>Built with</strong> Streamlit + Azure OpenAI GPT-4 Vision</p>
</div>
""", unsafe_allow_html=True)
