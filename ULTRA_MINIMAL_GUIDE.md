# Ultra-Minimal Interim Version - Session-Only with LLM Features

## Vision
Create the **simplest possible interim version** that:
- ✅ No database (local or cloud)
- ✅ No persistence (session memory only)
- ✅ No user accounts/authentication
- ✅ Profile stored in session state (lost on refresh)
- ✅ Only LLM-powered features:
  - Food image scanning & detection
  - Nutrition analysis
  - Personalized nutrition coaching (as paragraphs, not chat)

---

## What's Kept vs Removed

### ❌ COMPLETELY REMOVED
- Authentication system (local_auth.py, auth.py)
- Database (local_database.py, database.py)
- Meal history/logging
- Analytics & trends
- Meal history page
- Gamification
- Restaurant analyzer
- Coaching assistant (chat version)

### ✅ KEPT - LLM Features Only
- Food image recognition (photo upload)
- Nutrition analysis (text analysis)
- Macro/calorie breakdown
- Nutritional recommendations
- Personalized coaching tips (simple paragraphs)

### ✅ KEPT - UI Only
- Profile page (session-only)
- Food detection page
- Nutrition analysis page
- Coaching tips page

---

## New Architecture

```
ULTRA-MINIMAL INTERIM:

┌─────────────────────────────────┐
│      Streamlit App              │
├─────────────────────────────────┤
│  1. Profile Setup (Session)     │
│     - Age, health, goals        │
│     - Stored in st.session_state│
│     - Lost on refresh           │
├─────────────────────────────────┤
│  2. Food Detector               │
│     - Upload image              │
│     - Azure OpenAI Vision       │
│     - Real-time detection       │
├─────────────────────────────────┤
│  3. Nutrition Analysis          │
│     - Text or image analysis    │
│     - Azure OpenAI GPT          │
│     - Macro breakdown           │
├─────────────────────────────────┤
│  4. Nutrition Coach             │
│     - Personalized tips         │
│     - Based on profile          │
│     - Simple paragraphs         │
└─────────────────────────────────┘
```

---

## File Structure (Extremely Minimal)

```
eatwise_interim_minimal/
├── app.py                          # Single main file
├── config.py                       # Config + constants
├── nutrition_analyzer.py           # KEEP - LLM analysis
├── requirements.txt                # Streamlit + OpenAI only
├── README.md                       # Usage guide
└── .env                            # OpenAI API key
```

**Total Python files: Just 3!**

---

## Components Breakdown

### 1. `app.py` (Ultra-Minimal)

```python
"""
Ultra-Minimal EatWise - LLM-Only Session-Based
No database, no persistence, no authentication
"""

import streamlit as st
from datetime import datetime
from nutrition_analyzer import NutritionAnalyzer
from config import APP_NAME, OPENAI_API_KEY

# Initialize session state
def init_session():
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "age_group": None,
            "health_conditions": [],
            "dietary_preferences": [],
            "health_goal": None
        }
    if "current_analysis" not in st.session_state:
        st.session_state.current_analysis = None

init_session()

st.set_page_config(page_title=APP_NAME, layout="wide")

# Sidebar: Profile setup
with st.sidebar:
    st.header("👤 Your Profile (Session-Only)")
    st.info("Profile is stored in memory only. It will be reset when you refresh the page.")
    
    st.session_state.profile["age_group"] = st.selectbox(
        "Age Group",
        ["20-25", "26-35", "36-45", "46-55", "56+", "Not specified"]
    )
    
    st.session_state.profile["health_conditions"] = st.multiselect(
        "Health Conditions",
        ["Diabetes", "Hypertension", "Heart Disease", "Celiac", "None"],
        default=st.session_state.profile.get("health_conditions", ["None"])
    )
    
    st.session_state.profile["dietary_preferences"] = st.multiselect(
        "Dietary Preferences",
        ["Vegetarian", "Vegan", "Gluten-Free", "Keto", "Paleo", "None"],
        default=st.session_state.profile.get("dietary_preferences", ["None"])
    )
    
    st.session_state.profile["health_goal"] = st.selectbox(
        "Health Goal",
        ["Weight Loss", "Weight Gain", "Muscle Building", "Maintain Health", "Not specified"]
    )

# Main content
st.title("🥗 EatWise - Food Intelligence")
st.markdown("Powered by AI • No Account Needed • No Data Stored")

# Tabs for features
tab1, tab2, tab3 = st.tabs(["🔍 Scan Food", "📊 Analyze Nutrition", "💡 Get Coaching"])

with tab1:
    st.header("Food Detection & Recognition")
    uploaded_file = st.file_uploader("Upload a food photo", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file)
        
        if st.button("🔍 Detect Food"):
            with st.spinner("Analyzing food..."):
                analyzer = NutritionAnalyzer()
                detection = analyzer.detect_food_from_image(uploaded_file)
                st.session_state.current_analysis = detection
                
                st.success("Food detected!")
                st.write(f"**Detected Foods:** {detection.get('foods', [])}")
                st.write(f"**Confidence:** {detection.get('confidence', 0):.1%}")

with tab2:
    st.header("Nutrition Analysis")
    
    # Option 1: Analyze uploaded food
    if st.session_state.current_analysis:
        st.info("📸 Analyzing the food you just uploaded...")
        foods = st.session_state.current_analysis.get("foods", [])
        
        analysis = st.session_state.current_analysis.get("analysis", {})
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Calories", f"{analysis.get('calories', 0):.0f}")
        col2.metric("Protein", f"{analysis.get('protein', 0):.1f}g")
        col3.metric("Carbs", f"{analysis.get('carbs', 0):.1f}g")
        col4.metric("Fat", f"{analysis.get('fat', 0):.1f}g")
        
        st.subheader("Health Notes")
        st.write(analysis.get("health_notes", ""))
    
    # Option 2: Manual text entry
    st.divider()
    st.subheader("Or describe your meal manually")
    meal_description = st.text_area("Describe what you ate", placeholder="e.g., Grilled chicken breast with rice and broccoli")
    
    if st.button("📊 Analyze Meal"):
        with st.spinner("Analyzing nutrition..."):
            analyzer = NutritionAnalyzer()
            analysis = analyzer.analyze_text_meal(meal_description)
            st.session_state.current_analysis = analysis
            
            st.success("Analysis complete!")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Calories", f"{analysis.get('calories', 0):.0f}")
            col2.metric("Protein", f"{analysis.get('protein', 0):.1f}g")
            col3.metric("Carbs", f"{analysis.get('carbs', 0):.1f}g")
            col4.metric("Fat", f"{analysis.get('fat', 0):.1f}g")
            
            st.subheader("Health Notes")
            st.write(analysis.get("health_notes", ""))

with tab3:
    st.header("💡 Personalized Nutrition Coaching")
    
    if not st.session_state.profile["age_group"]:
        st.warning("⚠️ Please set up your profile in the sidebar first")
    else:
        if st.session_state.current_analysis:
            st.info("📊 Generating coaching based on your latest meal analysis...")
        
        st.subheader("Your Personalized Nutrition Tips")
        
        with st.spinner("Generating coaching..."):
            analyzer = NutritionAnalyzer()
            coaching = analyzer.get_personalized_coaching(
                profile=st.session_state.profile,
                meal_analysis=st.session_state.current_analysis
            )
            
            st.markdown(coaching)

# Footer
st.divider()
st.caption("🔐 Privacy: No account needed • No data stored • No tracking")
st.caption(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
```

### 2. `nutrition_analyzer.py` (Simplified LLM)

```python
"""
Nutrition Analyzer - LLM-Powered Features Only
No database, just API calls to OpenAI
"""

from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
import json
from typing import Dict, List, Optional
import base64
import streamlit as st

class NutritionAnalyzer:
    """Analyzes nutrition using Azure OpenAI Vision and GPT"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-10-01-preview",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        self.deployment = AZURE_OPENAI_DEPLOYMENT
    
    def detect_food_from_image(self, image_file) -> Dict:
        """Detect food items from image using Vision API"""
        try:
            # Convert image to base64
            image_data = base64.b64encode(image_file.read()).decode()
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this food image and provide:
1. List of detected food items (be specific about portions when visible)
2. Approximate portion sizes
3. Confidence level (0-100%)

Format as JSON with keys: foods (list), portions (list), confidence (number 0-100)"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            
            # Try to parse JSON, fallback to text parsing
            try:
                result = json.loads(result_text)
            except:
                result = {
                    "foods": ["Unable to parse, see raw response"],
                    "confidence": 0,
                    "raw_response": result_text
                }
            
            # Get nutrition analysis for detected foods
            foods_str = ", ".join(result.get("foods", []))
            analysis = self.analyze_text_meal(foods_str)
            result["analysis"] = analysis
            
            return result
            
        except Exception as e:
            st.error(f"Error analyzing image: {str(e)}")
            return {"error": str(e)}
    
    def analyze_text_meal(self, meal_description: str) -> Dict:
        """Analyze meal nutrition from text description"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Analyze the nutrition of this meal: "{meal_description}"

Provide a JSON response with:
- calories (number)
- protein (grams)
- carbs (grams)
- fat (grams)
- fiber (grams)
- sodium (mg)
- sugar (grams)
- healthiness_score (0-100)
- health_notes (brief paragraph about this meal)

Format as JSON."""
                    }
                ],
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content
            
            try:
                result = json.loads(result_text)
            except:
                # Fallback: create default structure
                result = {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "fiber": 0,
                    "sodium": 0,
                    "sugar": 0,
                    "healthiness_score": 50,
                    "health_notes": result_text
                }
            
            return result
            
        except Exception as e:
            st.error(f"Error analyzing meal: {str(e)}")
            return {"error": str(e)}
    
    def get_personalized_coaching(self, profile: Dict, meal_analysis: Optional[Dict] = None) -> str:
        """Generate personalized nutrition coaching based on profile"""
        try:
            # Build coaching prompt
            coaching_prompt = f"""Based on this user profile and their meal, provide personalized nutrition coaching.

USER PROFILE:
- Age Group: {profile.get('age_group', 'Not specified')}
- Health Conditions: {', '.join(profile.get('health_conditions', ['None']))}
- Dietary Preferences: {', '.join(profile.get('dietary_preferences', ['None']))}
- Health Goal: {profile.get('health_goal', 'Not specified')}
"""
            
            if meal_analysis:
                coaching_prompt += f"""

THEIR LATEST MEAL:
- Calories: {meal_analysis.get('calories', 'Unknown')}
- Protein: {meal_analysis.get('protein', 'Unknown')}g
- Carbs: {meal_analysis.get('carbs', 'Unknown')}g
- Fat: {meal_analysis.get('fat', 'Unknown')}g

Provide 2-3 specific, actionable coaching tips based on their health goal and the meal they just had."""
            else:
                coaching_prompt += """

Provide 2-3 personalized nutrition tips based on their profile and health goal."""
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "user",
                        "content": coaching_prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            coaching_text = response.choices[0].message.content
            return coaching_text
            
        except Exception as e:
            return f"Error generating coaching: {str(e)}"
```

### 3. `config.py` (Simplified)

```python
"""
Configuration - Ultra-Minimal Version
"""
import os
from dotenv import load_dotenv

load_dotenv()

# App
APP_NAME = "EatWise Minimal"
APP_DESCRIPTION = "AI Food Intelligence - No Database, No Login"

# Azure OpenAI
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# Nutrition defaults
CALORIE_TARGET = 2000
PROTEIN_TARGET = 50
```

---

## Requirements.txt

```
streamlit>=1.40.0
python-dotenv==1.0.0
openai==1.3.5
pillow>=8.0.0
```

---

## What Gets Removed

### Files to Delete:
- `auth.py` - No authentication
- `database.py` - No database
- `local_auth.py` - Not needed
- `local_database.py` - Not needed
- `recommender.py` - No recommendations
- `coaching_assistant.py` - Replaced with simple paragraphs
- `restaurant_analyzer.py` - Not needed
- `gamification.py` - Not needed
- `nutrition_components.py` - Simplify to basic Streamlit
- `utils.py` - Most utilities not needed
- `constants.py` - Minimal constants only

### Functions to Remove from nutrition_analyzer.py:
- Everything except food detection and analysis

---

## User Flow (Ultra-Minimal)

```
User Opens App
    ↓
Set Profile in Sidebar (Age, Health, Goals)
    ↓
Three Options:
├─→ Upload Food Photo → Detect & Analyze
├─→ Type Food Description → Analyze
└─→ Get Personalized Coaching Tips (Based on Latest Meal + Profile)
    ↓
No Save, No History, No Login
    ↓
Refresh Page = Fresh Start
```

---

## Storage & Data

### In Memory (Session State):
```
st.session_state = {
    "profile": {
        "age_group": "26-35",
        "health_conditions": ["Diabetes"],
        "dietary_preferences": ["Vegetarian"],
        "health_goal": "Weight Loss"
    },
    "current_analysis": {
        "foods": ["Salad with Chicken"],
        "calories": 450,
        "protein": 45,
        ...
    }
}
```

### NOT Stored Anywhere:
- ❌ No database
- ❌ No files
- ❌ No cloud
- ❌ No user accounts
- ❌ No meal history

---

## Key Differences from Original

| Feature | Original | Minimal |
|---------|----------|---------|
| Login | Required | None |
| Database | Supabase | None |
| Data Storage | Permanent | Session only |
| User Accounts | Yes | No |
| Meal History | Yes | No |
| Analytics | Yes | No |
| Gamification | Yes | No |
| Chat Coaching | Yes | Paragraph coaching |
| Features | 8+ | 3 (Food detect, Nutrition, Coaching) |
| Python Files | 12+ | 3 |
| Dependencies | 10+ | 3 |
| Setup Time | 30 min | 5 min |
| Complexity | High | Minimal |

---

## Implementation Steps

### Step 1: Keep Only Essential
- Delete all files mentioned above
- Keep: `app.py`, `nutrition_analyzer.py`, `config.py`, `requirements.txt`, `.env`

### Step 2: Rewrite app.py
- Use only Streamlit
- Session state for profile
- 3 tabs for 3 features
- No database imports

### Step 3: Simplify nutrition_analyzer.py
- Keep only: `detect_food_from_image()`, `analyze_text_meal()`, `get_personalized_coaching()`
- Remove all database functions

### Step 4: Test
```bash
streamlit run app.py
```

---

## Benefits of Ultra-Minimal Approach

✅ **Simplest possible interim version**
✅ **No database setup needed**
✅ **No user authentication**
✅ **No persistence concerns**
✅ **Pure LLM focus** (OpenAI calls)
✅ **Easy to understand**
✅ **Fast to develop**
✅ **Easy to test**
✅ **No data privacy concerns**
✅ **Easy to expand later**

---

## Example Session

```
User opens app
├─ Sets age: 26-35
├─ Sets conditions: Diabetes
├─ Sets preferences: Vegetarian
├─ Sets goal: Weight Loss
│
├─ Uploads photo of meal
├─ App detects: "Pasta Primavera"
├─ Analysis shows: 550 cal, 18g protein, 75g carbs
│
├─ Gets coaching:
│   "Based on your diabetic management and vegetarian diet,
│    this meal is high in carbs. Consider reducing portion size
│    or adding more protein. Good choice on vegetables though!"
│
└─ Refreshes page → Profile & analysis both gone
```

---

## Deployment

### Local:
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud:
```bash
git push to GitHub
Deploy normally
No credentials needed (except .env with OpenAI key)
No database to setup
```

---

## This is Perfect For:

✅ True MVP/interim submission
✅ Proof of concept for LLM capabilities
✅ Focus on AI features only
✅ No infrastructure complexity
✅ Zero setup required
✅ Easy to test & verify
✅ Easy to expand later

---

## Future Expansion Path

If you later want to add persistence:
1. Add `local_database.py` for session storage
2. Add accounts/login
3. Add meal history
4. Add analytics
5. Add gamification

But starts completely minimal!

