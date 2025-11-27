# Ultra-Minimal Implementation Guide

## Overview

Transform your EatWise into the **simplest possible interim version**:
- **3 Python files** (down from 12+)
- **3 Streamlit tabs** (Food Detect, Nutrition, Coaching)
- **Session-only storage** (no database, no login)
- **LLM-powered** (OpenAI Vision + GPT)
- **5-minute setup**

---

## Step 1: Clean Up (Delete Files)

Delete these files from your project:

```
❌ Delete completely:
- auth.py
- database.py
- local_auth.py
- local_database.py
- recommender.py
- coaching_assistant.py
- restaurant_analyzer.py
- gamification.py
- nutrition_components.py
- utils.py (or keep minimal version)
- constants.py (consolidate into config.py)
```

---

## Step 2: Create New Simple app.py

Create a brand new `app.py` using the code from `ULTRA_MINIMAL_GUIDE.md` Section "1. app.py (Ultra-Minimal)"

Key points:
- Remove all imports except Streamlit and NutritionAnalyzer
- Create session state for profile only
- 3 tabs: Food Detector, Nutrition Analysis, Coaching
- No login, no database, no history

---

## Step 3: Simplify nutrition_analyzer.py

Keep only these 3 methods from your existing nutrition_analyzer.py:

```python
def detect_food_from_image(self, image_file) -> Dict:
    # Detect food from uploaded photo

def analyze_text_meal(self, meal_description: str) -> Dict:
    # Analyze nutrition from text description

def get_personalized_coaching(self, profile: Dict, meal_analysis: Optional[Dict] = None) -> str:
    # Generate personalized coaching tips
```

Use the implementation from `ULTRA_MINIMAL_GUIDE.md`

---

## Step 4: Simplify config.py

Replace config.py with minimal version:

```python
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "EatWise Minimal"
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
```

---

## Step 5: Update requirements.txt

Replace with minimal dependencies:

```
streamlit>=1.40.0
python-dotenv==1.0.0
openai==1.3.5
pillow>=8.0.0
```

Remove:
- supabase
- pandas
- plotly
- requests
- All database-related packages

---

## Step 6: Test

```bash
# Activate venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run app
streamlit run app.py

# Test:
# 1. Set profile in sidebar
# 2. Upload food photo
# 3. Analyze meal
# 4. Get coaching tips
# 5. Refresh page → Everything resets ✓
```

---

## File Structure After Cleanup

```
Your Project:
├── app.py                          ✅ NEW (simpler version)
├── config.py                       ✅ SIMPLIFIED
├── nutrition_analyzer.py           ✅ SIMPLIFIED (3 methods only)
├── requirements.txt                ✅ UPDATED (minimal)
├── .env                            (unchanged)
├── venv/                           (unchanged)
├── ULTRA_MINIMAL_GUIDE.md          (this guide)
├── README.md                       (update if needed)
│
├── ❌ DELETED FILES:
│   ├── auth.py
│   ├── database.py
│   ├── local_auth.py
│   ├── local_database.py
│   ├── recommender.py
│   ├── coaching_assistant.py
│   ├── restaurant_analyzer.py
│   ├── gamification.py
│   ├── nutrition_components.py
│   └── utils.py
│
└── docs/                           (keep for reference)
```

---

## Code Changes Needed

### 1. app.py - Complete Rewrite

```python
import streamlit as st
from datetime import datetime
from nutrition_analyzer import NutritionAnalyzer
from config import APP_NAME

# Initialize session
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

# Sidebar for profile
with st.sidebar:
    st.header("👤 Your Profile")
    st.info("Session-only storage (resets on refresh)")
    
    st.session_state.profile["age_group"] = st.selectbox(
        "Age", ["20-25", "26-35", "36-45", "46-55", "56+", "Not specified"]
    )
    st.session_state.profile["health_conditions"] = st.multiselect(
        "Health Conditions",
        ["Diabetes", "Hypertension", "Celiac", "None"],
        default=["None"]
    )
    st.session_state.profile["dietary_preferences"] = st.multiselect(
        "Dietary Preferences",
        ["Vegetarian", "Vegan", "Gluten-Free", "None"],
        default=["None"]
    )
    st.session_state.profile["health_goal"] = st.selectbox(
        "Health Goal",
        ["Weight Loss", "Weight Gain", "Maintain Health", "Not specified"]
    )

# Main content
st.title("🥗 EatWise Minimal")
st.markdown("AI Food Intelligence • No Login • No Database")

tab1, tab2, tab3 = st.tabs(["🔍 Scan Food", "📊 Analyze", "💡 Coach"])

with tab1:
    st.header("Food Detection")
    uploaded_file = st.file_uploader("Upload food photo", type=["jpg", "jpeg", "png"])
    
    if uploaded_file and st.button("🔍 Detect"):
        with st.spinner("Analyzing..."):
            analyzer = NutritionAnalyzer()
            result = analyzer.detect_food_from_image(uploaded_file)
            st.session_state.current_analysis = result
            
            st.image(uploaded_file)
            st.write(f"Foods: {result.get('foods', [])}")

with tab2:
    st.header("Nutrition Analysis")
    
    meal = st.text_area("Describe meal or foods", placeholder="e.g., Grilled chicken with rice")
    
    if st.button("📊 Analyze"):
        with st.spinner("Analyzing..."):
            analyzer = NutritionAnalyzer()
            analysis = analyzer.analyze_text_meal(meal)
            st.session_state.current_analysis = analysis
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Cal", f"{analysis.get('calories', 0):.0f}")
            col2.metric("Protein", f"{analysis.get('protein', 0):.0f}g")
            col3.metric("Carbs", f"{analysis.get('carbs', 0):.0f}g")
            col4.metric("Fat", f"{analysis.get('fat', 0):.0f}g")
            
            st.write(analysis.get("health_notes", ""))

with tab3:
    st.header("Personalized Coaching")
    
    if not st.session_state.profile["age_group"]:
        st.warning("Set profile in sidebar first")
    else:
        if st.button("💡 Get Tips"):
            with st.spinner("Generating..."):
                analyzer = NutritionAnalyzer()
                coaching = analyzer.get_personalized_coaching(
                    profile=st.session_state.profile,
                    meal_analysis=st.session_state.current_analysis
                )
                st.markdown(coaching)

st.divider()
st.caption("🔐 No data stored • No tracking • No account needed")
```

### 2. nutrition_analyzer.py - Keep Only 3 Methods

Keep only these:
- `detect_food_from_image()`
- `analyze_text_meal()`
- `get_personalized_coaching()`

Remove everything else (meal logging, database queries, etc.)

### 3. config.py - Minimal Version

```python
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "EatWise Minimal"
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
```

---

## Testing Checklist

```
After Implementation:

□ Project starts: streamlit run app.py
□ No import errors
□ Sidebar profile loads
□ Can select age/conditions/preferences
□ Can upload food photo
□ Food detection works
□ Can type meal description
□ Nutrition analysis works
□ Can get coaching tips
□ Refresh page → Profile/analysis resets ✓
□ No .env errors
□ No database connections attempted
```

---

## What User Experiences

```
1. Opens app
   ↓
2. Sets profile (age, health, goals) in sidebar
   ↓
3. Chooses action:
   - Upload food photo → See detection + nutrition
   - Type description → See nutrition
   - Get coaching tips based on profile
   ↓
4. All features powered by OpenAI
   ↓
5. Refresh page → Everything resets
```

---

## Environment Variables Needed

Your `.env` should have:

```
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

No Supabase credentials needed!

---

## Summary

| Aspect | Count |
|--------|-------|
| Python files | 3 |
| Lines of code | ~500 |
| Streamlit tabs | 3 |
| External APIs | 1 (OpenAI) |
| Database | 0 |
| User accounts | 0 |
| Persistence | 0 |
| Setup time | 5 min |
| Implementation time | 15 min |

---

## This Ultra-Minimal Version

✅ Focuses entirely on **LLM capabilities**
✅ **Zero database** complexity
✅ **Zero authentication** complexity
✅ **Session-only** profile storage
✅ **Instant refresh** → Clean state
✅ **Easy to understand** (3 tabs)
✅ **Easy to test** (no setup)
✅ **Easy to expand** (add persistence later)
✅ **Perfect interim submission** 🎯

---

## Next Steps

1. Delete all the files listed in Step 1
2. Create new app.py using code from ULTRA_MINIMAL_GUIDE.md
3. Simplify nutrition_analyzer.py (keep 3 methods)
4. Update config.py to minimal version
5. Update requirements.txt
6. Test with `streamlit run app.py`
7. Submit!

---

Done! You have a truly minimal, LLM-focused interim version! 🚀

