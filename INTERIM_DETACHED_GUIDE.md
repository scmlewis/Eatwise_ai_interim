# Interim Version: Complete Database Detachment Guide

## Goal
Create an interim version that is **completely detached from Supabase** using **local storage** instead, so the complete version can keep its full Supabase database untouched.

---

## Architecture Overview

### Current Architecture (Full Version)
```
Streamlit App → AuthManager (Supabase Auth) → DatabaseManager (Supabase DB) → Cloud
```

### Interim Architecture
```
Streamlit App → LocalAuth (Session-based) → LocalStorage (JSON/Pickle) → Local Files
```

---

## Implementation Strategy

You'll create **3 new files** that replace Supabase entirely:

1. `local_auth.py` - Simple session-based authentication (no Supabase)
2. `local_database.py` - JSON-based data storage (no Supabase)
3. `.env.local` - Local environment (optional, for testing)

Then **modify 2 files**:
- `app.py` - Use local auth/database imports
- `config.py` - Disable Supabase requirement

---

## Step 1: Create Local Authentication (`local_auth.py`)

This replaces `auth.py` with simple session-based auth:

```python
"""Local Authentication - No Supabase Required"""
import streamlit as st
import json
import os
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
import hashlib

class LocalAuthManager:
    """Simple local authentication without Supabase"""
    
    USERS_FILE = "data/users.json"
    
    def __init__(self):
        """Initialize local auth system"""
        os.makedirs("data", exist_ok=True)
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load users from JSON file"""
        if os.path.exists(self.USERS_FILE):
            try:
                with open(self.USERS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(self.USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password (simple - don't use in production)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def sign_up(self, email: str, password: str, full_name: str) -> Tuple[bool, str]:
        """Sign up a new user"""
        try:
            if email in self.users:
                return False, "Email already registered"
            
            user_id = hashlib.md5(email.encode()).hexdigest()[:12]
            
            self.users[email] = {
                "user_id": user_id,
                "email": email,
                "password_hash": self._hash_password(password),
                "full_name": full_name,
                "created_at": datetime.now().isoformat()
            }
            self._save_users()
            return True, user_id
        except Exception as e:
            return False, f"Sign up error: {str(e)}"
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Login user"""
        try:
            if email not in self.users:
                return False, "User not found", None
            
            user = self.users[email]
            if user["password_hash"] != self._hash_password(password):
                return False, "Invalid password", None
            
            user_data = {
                "user_id": user["user_id"],
                "email": user["email"],
                "full_name": user["full_name"]
            }
            return True, "Login successful", user_data
        except Exception as e:
            return False, f"Login error: {str(e)}", None
    
    def logout(self):
        """Logout user"""
        if "user" in st.session_state:
            del st.session_state["user"]
        if "user_id" in st.session_state:
            del st.session_state["user_id"]

def init_local_auth_session():
    """Initialize authentication session"""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)
```

---

## Step 2: Create Local Database (`local_database.py`)

This replaces `database.py` with JSON-based storage:

```python
"""Local Database - No Supabase Required"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import streamlit as st
import uuid

class LocalDatabaseManager:
    """Handles all database operations using local JSON storage"""
    
    DATA_DIR = "data"
    
    def __init__(self):
        """Initialize local database"""
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(f"{self.DATA_DIR}/users", exist_ok=True)
    
    def _get_user_file(self, user_id: str, filename: str) -> str:
        """Get user-specific file path"""
        return f"{self.DATA_DIR}/users/{user_id}/{filename}"
    
    def _ensure_user_dir(self, user_id: str):
        """Create user directory if it doesn't exist"""
        os.makedirs(f"{self.DATA_DIR}/users/{user_id}", exist_ok=True)
    
    def _load_json(self, filepath: str) -> Any:
        """Load JSON file"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_json(self, filepath: str, data: Any):
        """Save JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    # ==================== HEALTH PROFILE ====================
    
    def create_health_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Create user health profile"""
        try:
            self._ensure_user_dir(user_id)
            
            profile = {
                "user_id": user_id,
                "full_name": profile_data.get("full_name", ""),
                "age_group": profile_data.get("age_group", ""),
                "gender": profile_data.get("gender", ""),
                "health_conditions": profile_data.get("health_conditions", []),
                "dietary_preferences": profile_data.get("dietary_preferences", []),
                "health_goal": profile_data.get("health_goal", ""),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self._save_json(self._get_user_file(user_id, "profile.json"), profile)
            st.success("Profile created successfully!")
            return True
        except Exception as e:
            st.error(f"Error creating health profile: {str(e)}")
            return False
    
    def get_health_profile(self, user_id: str) -> Optional[Dict]:
        """Get user health profile"""
        try:
            profile = self._load_json(self._get_user_file(user_id, "profile.json"))
            return profile if profile else None
        except Exception as e:
            st.error(f"Error fetching health profile: {str(e)}")
            return None
    
    def update_health_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Update user health profile"""
        try:
            profile = self.get_health_profile(user_id)
            if not profile:
                return self.create_health_profile(user_id, profile_data)
            
            profile.update({
                "full_name": profile_data.get("full_name", profile.get("full_name")),
                "age_group": profile_data.get("age_group", profile.get("age_group")),
                "gender": profile_data.get("gender", profile.get("gender")),
                "health_conditions": profile_data.get("health_conditions", profile.get("health_conditions")),
                "dietary_preferences": profile_data.get("dietary_preferences", profile.get("dietary_preferences")),
                "health_goal": profile_data.get("health_goal", profile.get("health_goal")),
                "updated_at": datetime.now().isoformat()
            })
            
            self._save_json(self._get_user_file(user_id, "profile.json"), profile)
            st.success("Profile updated successfully!")
            return True
        except Exception as e:
            st.error(f"Error updating health profile: {str(e)}")
            return False
    
    # ==================== MEAL LOGGING ====================
    
    def log_meal(self, meal_data: Dict) -> bool:
        """Log a new meal"""
        try:
            user_id = meal_data.get("user_id")
            self._ensure_user_dir(user_id)
            
            # Load existing meals
            meals = self._load_json(self._get_user_file(user_id, "meals.json"))
            if not isinstance(meals, list):
                meals = []
            
            # Add new meal
            meal = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "meal_name": meal_data.get("meal_name", ""),
                "description": meal_data.get("description", ""),
                "meal_type": meal_data.get("meal_type", ""),
                "nutrition": meal_data.get("nutrition", {}),
                "healthiness_score": meal_data.get("healthiness_score", 0),
                "health_notes": meal_data.get("health_notes", ""),
                "logged_at": meal_data.get("logged_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat()
            }
            
            meals.append(meal)
            self._save_json(self._get_user_file(user_id, "meals.json"), meals)
            st.success("Meal saved successfully!")
            return True
        except Exception as e:
            st.error(f"Error logging meal: {str(e)}")
            return False
    
    def get_meals_by_date(self, user_id: str, meal_date: date) -> List[Dict]:
        """Get meals for a specific date"""
        try:
            meals = self._load_json(self._get_user_file(user_id, "meals.json"))
            if not isinstance(meals, list):
                return []
            
            date_str = meal_date.isoformat()
            return [m for m in meals if m.get("logged_at", "").startswith(date_str)]
        except Exception as e:
            st.error(f"Error fetching meals: {str(e)}")
            return []
    
    def get_meals_in_range(self, user_id: str, start_date: date, end_date: date) -> List[Dict]:
        """Get meals within a date range"""
        try:
            meals = self._load_json(self._get_user_file(user_id, "meals.json"))
            if not isinstance(meals, list):
                return []
            
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            
            filtered = []
            for m in meals:
                logged = m.get("logged_at", "")[:10]
                if start_str <= logged <= end_str:
                    filtered.append(m)
            
            return sorted(filtered, key=lambda x: x.get("logged_at", ""))
        except Exception as e:
            st.error(f"Error fetching meals: {str(e)}")
            return []
    
    def get_recent_meals(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent meals"""
        try:
            meals = self._load_json(self._get_user_file(user_id, "meals.json"))
            if not isinstance(meals, list):
                return []
            return sorted(meals, key=lambda x: x.get("logged_at", ""), reverse=True)[:limit]
        except Exception as e:
            st.error(f"Error fetching recent meals: {str(e)}")
            return []
    
    def update_meal(self, meal_id: str, meal_data: Dict) -> bool:
        """Update meal record"""
        try:
            user_id = meal_data.get("user_id")
            meals = self._load_json(self._get_user_file(user_id, "meals.json"))
            
            for meal in meals:
                if meal.get("id") == meal_id:
                    meal.update(meal_data)
                    meal["updated_at"] = datetime.now().isoformat()
                    self._save_json(self._get_user_file(user_id, "meals.json"), meals)
                    return True
            
            return False
        except Exception as e:
            st.error(f"Error updating meal: {str(e)}")
            return False
    
    def delete_meal(self, meal_id: str, user_id: str) -> bool:
        """Delete meal record"""
        try:
            meals = self._load_json(self._get_user_file(user_id, "meals.json"))
            meals = [m for m in meals if m.get("id") != meal_id]
            self._save_json(self._get_user_file(user_id, "meals.json"), meals)
            return True
        except Exception as e:
            st.error(f"Error deleting meal: {str(e)}")
            return False
    
    # ==================== MEAL HISTORY & TRENDS ====================
    
    def get_daily_nutrition_summary(self, user_id: str, meal_date: date) -> Dict[str, float]:
        """Calculate daily nutrition summary"""
        meals = self.get_meals_by_date(user_id, meal_date)
        
        summary = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "sodium": 0,
            "sugar": 0,
            "fiber": 0,
        }
        
        for meal in meals:
            nutrition = meal.get("nutrition", {})
            summary["calories"] += nutrition.get("calories", 0)
            summary["protein"] += nutrition.get("protein", 0)
            summary["carbs"] += nutrition.get("carbs", 0)
            summary["fat"] += nutrition.get("fat", 0)
            summary["sodium"] += nutrition.get("sodium", 0)
            summary["sugar"] += nutrition.get("sugar", 0)
            summary["fiber"] += nutrition.get("fiber", 0)
        
        return summary
    
    def get_weekly_nutrition_summary(self, user_id: str, end_date: date) -> Dict:
        """Calculate weekly nutrition summary"""
        from datetime import timedelta
        
        start_date = end_date - timedelta(days=6)
        meals = self.get_meals_in_range(user_id, start_date, end_date)
        
        weekly_summary = {}
        for meal in meals:
            meal_date = meal.get("logged_at", "").split("T")[0]
            
            if meal_date not in weekly_summary:
                weekly_summary[meal_date] = {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "sodium": 0,
                    "sugar": 0,
                    "fiber": 0,
                    "meal_count": 0,
                }
            
            nutrition = meal.get("nutrition", {})
            weekly_summary[meal_date]["calories"] += nutrition.get("calories", 0)
            weekly_summary[meal_date]["protein"] += nutrition.get("protein", 0)
            weekly_summary[meal_date]["carbs"] += nutrition.get("carbs", 0)
            weekly_summary[meal_date]["fat"] += nutrition.get("fat", 0)
            weekly_summary[meal_date]["sodium"] += nutrition.get("sodium", 0)
            weekly_summary[meal_date]["sugar"] += nutrition.get("sugar", 0)
            weekly_summary[meal_date]["fiber"] += nutrition.get("fiber", 0)
            weekly_summary[meal_date]["meal_count"] += 1
        
        return weekly_summary
    
    def save_food_history(self, user_id: str, food_item: Dict) -> bool:
        """Save food item to user history"""
        try:
            self._ensure_user_dir(user_id)
            history = self._load_json(self._get_user_file(user_id, "food_history.json"))
            
            if not isinstance(history, list):
                history = []
            
            food_item["id"] = str(uuid.uuid4())
            food_item["last_used"] = datetime.now().isoformat()
            history.append(food_item)
            
            self._save_json(self._get_user_file(user_id, "food_history.json"), history)
            return True
        except Exception as e:
            st.error(f"Error saving food history: {str(e)}")
            return False
    
    def get_food_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get user's food history"""
        try:
            history = self._load_json(self._get_user_file(user_id, "food_history.json"))
            if not isinstance(history, list):
                return []
            return sorted(history, key=lambda x: x.get("last_used", ""), reverse=True)[:limit]
        except Exception as e:
            st.error(f"Error fetching food history: {str(e)}")
            return []
```

---

## Step 3: Update `config.py`

Make Supabase optional:

```python
"""Configuration for EatWise"""
import os
from dotenv import load_dotenv

load_dotenv()

# App Configuration
APP_NAME = "EatWise (Interim Version)"
APP_DESCRIPTION = "AI-Powered Nutrition Hub - Local Version"

# Supabase Configuration - OPTIONAL for interim version
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
USE_SUPABASE = SUPABASE_URL and SUPABASE_KEY  # Only use if credentials provided

# ... rest of config remains the same
```

---

## Step 4: Update `app.py` Imports

Change these lines at the top of `app.py`:

**OLD:**
```python
from auth import AuthManager, init_auth_session, is_authenticated
from database import DatabaseManager
```

**NEW:**
```python
# For interim version, use local storage instead of Supabase
from local_auth import LocalAuthManager as AuthManager, init_local_auth_session as init_auth_session, is_authenticated
from local_database import LocalDatabaseManager as DatabaseManager
```

---

## Step 5: Update Requirements (Optional)

If using interim version, you can remove Supabase from `requirements.txt`:

**For interim version only:**
```
streamlit>=1.40.0
python-dotenv==1.0.0
openai==1.3.5
pandas==2.2.3
requests==2.31.0
plotly==5.24.1
python-dateutil==2.8.2
pytz==2024.1
streamlit-option-menu==0.4.0
pillow>=8.0.0
```

(Remove `supabase==2.0.3`)

---

## Data Storage Structure

Interim version creates this local structure:

```
data/
├── users.json                          # All user credentials
└── users/
    └── {user_id}/
        ├── profile.json               # User health profile
        ├── meals.json                 # All meals logged
        └── food_history.json          # Food history cache
```

Example `data/users.json`:
```json
{
  "test@example.com": {
    "user_id": "abc123def456",
    "email": "test@example.com",
    "password_hash": "...",
    "full_name": "John Doe",
    "created_at": "2025-11-28T..."
  }
}
```

Example `data/users/abc123def456/profile.json`:
```json
{
  "user_id": "abc123def456",
  "full_name": "John Doe",
  "age_group": "26-35",
  "health_conditions": ["Diabetes"],
  "dietary_preferences": ["Vegetarian"],
  "health_goal": "Weight Loss",
  "created_at": "2025-11-28T...",
  "updated_at": "2025-11-28T..."
}
```

---

## Benefits of This Approach

✅ **Complete Separation** - Interim version never touches Supabase  
✅ **Local Storage** - All data stored in JSON files in `data/` folder  
✅ **No Database Setup** - No SQL migrations needed  
✅ **Easy Distribution** - Just run `streamlit run app.py`  
✅ **Easy Cleanup** - Delete `data/` folder to reset  
✅ **Full Version Untouched** - Production database remains pristine  
✅ **Easy to Revert** - Keep both versions in git branches  

---

## Deployment Options

### Option 1: Local Testing
```bash
python -m streamlit run app.py
```
- Data stored in local `data/` folder
- Perfect for testing

### Option 2: Streamlit Cloud (Interim Only)
```bash
# Push to GitHub with local_auth.py and local_database.py
# .gitignore: data/
streamlit run app.py
```
- Data stored on user's local filesystem
- Each deployment gets fresh data

---

## Known Limitations (Interim)

- ❌ No real authentication (password stored as hash locally)
- ❌ No multi-device sync
- ❌ No data backup/recovery
- ❌ No sharing between users
- ❌ Data lost if `data/` folder deleted

These limitations are expected for an interim version.

---

## Migration Path to Full Version

When ready to migrate to full version:

1. Keep this branch as `interim-detached`
2. Switch to main branch with Supabase
3. Run Supabase migrations
4. Update imports back to Supabase versions
5. Run data migration script if needed

---

## Next Steps

1. Create `local_auth.py` with the code above
2. Create `local_database.py` with the code above
3. Update `config.py` to make Supabase optional
4. Update imports in `app.py`
5. Test by running `streamlit run app.py`
6. Create test user and log a meal
7. Verify data appears in `data/` folder

This way your complete Supabase database remains completely untouched!

