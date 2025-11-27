# Visual Architecture - Interim Detached Version

## System Comparison

### Full Version (Current - with Supabase)
```
┌─────────────────────────────────────┐
│     Streamlit Web App               │
│  (app.py, nutrition_analyzer, etc)  │
└──────────────┬──────────────────────┘
               │
        ┌──────▼──────┐
        │  AuthManager│ ◄─── imports from auth.py
        │(auth.py)    │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │ DatabaseMgr │ ◄─── imports from database.py
        │(database.py)│
        └──────┬──────┘
               │
      ┌────────▼────────┐
      │   Supabase      │
      │   (Cloud)       │
      │ ┌─────────────┐ │
      │ │ Auth Service│ │
      │ ├─────────────┤ │
      │ │ PostgreSQL  │ │
      │ │ Database    │ │
      │ └─────────────┘ │
      └─────────────────┘
         Your Credentials
         (Stored in .env)
```

---

### Interim Version (New - No Supabase)
```
┌─────────────────────────────────────┐
│     Streamlit Web App               │
│  (app.py, nutrition_analyzer, etc)  │
└──────────────┬──────────────────────┘
               │
      ┌────────▼────────┐
      │ USE_LOCAL_DB?   │
      │ (config.py)     │
      └────┬───────┬────┘
         T │       │ F
          ▼        ▼
    ┌─────────┐ ┌──────────┐
    │ Local   │ │ Supabase │
    │ Version │ │ Version  │
    └────┬────┘ └──────────┘
         │
    ┌────▼──────────┐
    │LocalAuthMgr   │ ◄─── imports from local_auth.py
    │(local_auth.py)│
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │LocalDatabaseMgr│ ◄─── imports from local_database.py
    │(local_database │
    └────┬───────────┘
         │
    ┌────▼──────────┐
    │  Local JSON   │
    │  Storage      │
    │ ┌───────────┐ │
    │ │ data/     │ │
    │ │ ├─users   │ │
    │ │ │ ├─user1 │ │
    │ │ │ │├─meals│ │
    │ │ │ │└─prof │ │
    │ │ │ └─user2 │ │
    │ │ │  ...    │ │
    │ └───────────┘ │
    └───────────────┘
       NO Internet
       NO Database
       Completely Local
```

---

## Code Flow Comparison

### Full Version (Supabase)
```
User Signup Flow:
1. User enters email/password in Streamlit
2. AuthManager.sign_up() called
3. Calls supabase.auth.sign_up(email, password)
4. Supabase validates & creates user account
5. Response returned to Streamlit
6. User data stored in PostgreSQL
7. Success message shown to user

Data Storage:
app.py → database.py → DatabaseManager
              ↓
     self.supabase.table("meals").insert()
              ↓
       Cloud PostgreSQL Database
```

### Interim Version (Local JSON)
```
User Signup Flow:
1. User enters email/password in Streamlit
2. LocalAuthManager.sign_up() called
3. Checks if email exists in data/users.json
4. If new, creates user object with hashed password
5. Appends to data/users.json file
6. Saves file locally
7. Success message shown to user

Data Storage:
app.py → local_database.py → LocalDatabaseManager
              ↓
     self._save_json(file_path, data)
              ↓
        Local JSON File (data/ folder)
```

---

## File Organization

### Before (Single Architecture)
```
Eatwise_ai_interim/
├── app.py          ◄─── Always uses Supabase
├── auth.py         ◄─── Supabase Auth only
├── database.py     ◄─── Supabase DB only
└── config.py       ◄─── Supabase config only
```

### After (Dual Architecture)
```
Eatwise_ai_interim/
├── app.py          ◄─── Switches based on config
├── config.py       ◄─── Has USE_LOCAL_DATABASE flag
│
├── auth.py         ◄─── Supabase Auth (full version)
├── database.py     ◄─── Supabase DB (full version)
│
├── local_auth.py   ◄─── Local Auth (interim version) NEW
├── local_database.py ◄─ Local DB (interim version) NEW
│
└── data/           ◄─── Created automatically
    ├── users.json
    └── users/
        └── {user_id}/
            ├── profile.json
            ├── meals.json
            └── food_history.json
```

---

## Configuration Switch

```
config.py:

┌──────────────────────────────────────┐
│ USE_LOCAL_DATABASE = True            │ ◄─── Change to True for interim
│                                      │
│ # If True:                          │
│ # - Uses local_auth.py              │
│ # - Uses local_database.py          │
│ # - Data stored in data/ folder     │
│ # - No Supabase needed              │
│                                      │
│ # If False:                         │
│ # - Uses auth.py                    │
│ # - Uses database.py                │
│ # - Data stored in Supabase cloud   │
│ # - Requires Supabase credentials   │
└──────────────────────────────────────┘

app.py:

┌──────────────────────────────────────────────────────┐
│ if USE_LOCAL_DATABASE:                              │
│     from local_auth import ...                       │
│     from local_database import ...                   │
│ else:                                               │
│     from auth import ...                            │
│     from database import ...                        │
└──────────────────────────────────────────────────────┘
```

---

## Data Structure

### Local Storage (Interim)
```
data/
├── users.json
│   └── {
│       "test@example.com": {
│           "user_id": "a1b2c3d4e5f6",
│           "password_hash": "5e884898...",
│           "full_name": "Test User",
│           "created_at": "2025-11-28T10:00:00"
│       }
│   }
│
└── users/a1b2c3d4e5f6/
    ├── profile.json
    │   └── {
    │       "user_id": "a1b2c3d4e5f6",
    │       "age_group": "26-35",
    │       "health_goal": "Weight Loss",
    │       "health_conditions": ["Diabetes"],
    │       ...
    │   }
    │
    ├── meals.json
    │   └── [
    │       {
    │           "id": "meal-uuid-123",
    │           "meal_name": "Chicken Salad",
    │           "nutrition": {"calories": 450, ...},
    │           "logged_at": "2025-11-28T12:00:00"
    │       },
    │       {
    │           "id": "meal-uuid-456",
    │           "meal_name": "Grilled Fish",
    │           ...
    │       }
    │   ]
    │
    └── food_history.json
        └── [food items]
```

### Cloud Storage (Full Version - Supabase)
```
Supabase Project
├── Auth Service
│   └── Users Table
│       ├── user1@email.com (hashed password)
│       └── user2@email.com (hashed password)
│
└── PostgreSQL Database
    ├── users
    │   └── user data
    ├── health_profiles
    │   └── health info
    ├── meals
    │   └── meal logs
    ├── food_history
    │   └── cached foods
    ├── daily_challenges
    │   └── gamification
    └── weekly_goals
        └── gamification
```

---

## Authentication Comparison

### Supabase Auth (Full Version)
```
┌─────────────┐
│  Streamlit  │
└──────┬──────┘
       │ send email/password
       │
┌──────▼──────────────────┐
│  Supabase Auth Service   │
│  (Cloud)                 │
│  ┌────────────────────┐  │
│  │ Hash password      │  │
│  │ Compare hashes     │  │
│  │ Issue session token│  │
│  │ Store in cloud DB  │  │
│  └────────────────────┘  │
└──────┬──────────────────┘
       │ return token
       │
┌──────▼──────┐
│  Streamlit  │
│  (Logged in)│
└─────────────┘
```

### Local Auth (Interim Version)
```
┌─────────────┐
│  Streamlit  │
└──────┬──────┘
       │ send email/password
       │
┌──────▼──────────────────┐
│  local_auth.py           │
│  (LocalAuthManager)      │
│  ┌────────────────────┐  │
│  │ Hash password      │  │
│  │ Compare with file  │  │
│  │ Set session state  │  │
│  │ Store in JSON file │  │
│  └────────────────────┘  │
└──────┬──────────────────┘
       │ return success
       │
┌──────▼──────┐
│  Streamlit  │
│  (Logged in)│
└─────────────┘

All operations are LOCAL (no network calls)
```

---

## Feature Availability

```
Core Features (Both Versions):
✅ Meal Logging
✅ Nutrition Analysis  
✅ Analytics & Trends
✅ Health Profile
✅ Meal History
✅ Food History Cache

Gamification (Full Only):
❌ XP/Leveling
❌ Daily Challenges
❌ Weekly Goals
❌ Badges
❌ Streaks

AI Features (Full Only):
❌ Nutrition Coaching
❌ Restaurant Analyzer
❌ Advanced Recommendations

Multi-Device (Full Only):
❌ Cloud Sync
❌ Multi-device Access
```

---

## Implementation Steps (Visual)

```
START
  │
  ├─ Step 1: Create local_auth.py ✅ DONE
  │
  ├─ Step 2: Create local_database.py ✅ DONE
  │
  ├─ Step 3: Edit config.py (1 line)
  │         USE_LOCAL_DATABASE = True
  │
  ├─ Step 4: Edit app.py (5 lines)
  │         Add conditional imports
  │
  ├─ Step 5: Run streamlit run app.py
  │
  ├─ Step 6: Test signup/login/meals
  │
  ├─ Step 7: Verify data/ folder
  │
  └─ DONE! Interim version ready! 🎉
```

---

## Switching Between Versions

```
Want Interim (Local)?
    ↓
config.py: USE_LOCAL_DATABASE = True
    ↓
Run: streamlit run app.py
    ↓
Use local_auth.py + local_database.py
    ↓
Data in data/ folder (local JSON)


Want Full Version (Supabase)?
    ↓
config.py: USE_LOCAL_DATABASE = False
    ↓
Run: streamlit run app.py
    ↓
Use auth.py + database.py
    ↓
Data in Supabase cloud (PostgreSQL)
```

---

## Summary

| Aspect | Interim | Full |
|--------|---------|------|
| **Storage** | Local JSON | Supabase Cloud |
| **Auth** | local_auth.py | Supabase Auth |
| **Database** | local_database.py | Supabase DB |
| **Config** | USE_LOCAL_DATABASE=True | USE_LOCAL_DATABASE=False |
| **Data Location** | data/ folder | Cloud server |
| **Multi-device** | ❌ No | ✅ Yes |
| **Persistence** | Session-based | Permanent |
| **Setup** | ✅ Zero | ⚙️ Config needed |
| **Features** | Core only | All features |

---

This visual architecture shows how simple the switch is:
- ✅ Same app.py code
- ✅ Same UI/UX
- ✅ Different backend implementation
- ✅ One config flag to switch

Perfect for an interim submission! 🚀

