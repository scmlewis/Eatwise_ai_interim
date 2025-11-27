# Exact Code Changes - Copy & Paste Guide

## Change 1: Update `config.py`

### Find this section (around line 5-8):

```python
# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

### Replace with:

```python
# Version Configuration
USE_LOCAL_DATABASE = True  # Set to False to use Supabase instead

# Supabase Configuration (only used if USE_LOCAL_DATABASE = False)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
```

---

## Change 2: Update imports in `app.py`

### Find this section (around line 10-15):

```python
from config import (
    APP_NAME, APP_DESCRIPTION, SUPABASE_URL, SUPABASE_KEY,
    DAILY_CALORIE_TARGET, DAILY_PROTEIN_TARGET, DAILY_CARBS_TARGET,
    DAILY_FAT_TARGET, DAILY_SODIUM_TARGET, DAILY_SUGAR_TARGET, 
    DAILY_FIBER_TARGET, AGE_GROUP_TARGETS, HEALTH_CONDITION_TARGETS, HEALTH_GOAL_TARGETS,
    AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
)
```

### Update to include USE_LOCAL_DATABASE:

```python
from config import (
    APP_NAME, APP_DESCRIPTION, SUPABASE_URL, SUPABASE_KEY,
    USE_LOCAL_DATABASE,
    DAILY_CALORIE_TARGET, DAILY_PROTEIN_TARGET, DAILY_CARBS_TARGET,
    DAILY_FAT_TARGET, DAILY_SODIUM_TARGET, DAILY_SUGAR_TARGET, 
    DAILY_FIBER_TARGET, AGE_GROUP_TARGETS, HEALTH_CONDITION_TARGETS, HEALTH_GOAL_TARGETS,
    AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
)
```

### Find these imports (around line 20-25):

```python
from auth import AuthManager, init_auth_session, is_authenticated
from database import DatabaseManager
```

### Replace with:

```python
# Choose authentication and database based on configuration
if USE_LOCAL_DATABASE:
    from local_auth import LocalAuthManager as AuthManager
    from local_auth import init_local_auth_session as init_auth_session
    from local_auth import is_authenticated
    from local_database import LocalDatabaseManager as DatabaseManager
else:
    from auth import AuthManager, init_auth_session, is_authenticated
    from database import DatabaseManager
```

---

## That's It!

No other changes needed. The app will now:

1. Use local JSON storage when `USE_LOCAL_DATABASE = True`
2. Use Supabase when `USE_LOCAL_DATABASE = False`

---

## To Switch Back to Supabase (Full Version)

Just change one line in `config.py`:

```python
USE_LOCAL_DATABASE = False  # Changed from True
```

That's all! No other code needs to change.

---

## Testing the Changes

### Test 1: Verify app starts
```bash
streamlit run app.py
```
- Should show login page
- No Supabase errors

### Test 2: Create account
- Sign up with `test@example.com` / `password123` / `Test User`
- Should succeed

### Test 3: Check data folder
```bash
ls data/
# Should show: users.json
```

### Test 4: Check user data
```bash
cat data/users.json
# Should show JSON with user credentials
```

### Test 5: Verify persistence
- Login
- Log a meal
- Refresh browser (Ctrl+R or Cmd+R)
- Meal should still be there

---

## File Locations

Make sure these files are in the same directory as `app.py`:

✅ `local_auth.py` - Already created for you
✅ `local_database.py` - Already created for you
✅ `config.py` - Modify as shown above
✅ `app.py` - Modify as shown above

---

## Troubleshooting

**Error: "ModuleNotFoundError: No module named 'local_auth'"**
- Make sure `local_auth.py` is in same folder as `app.py`
- Check file name spelling

**Error: "NameError: name 'USE_LOCAL_DATABASE' is not defined"**
- Make sure you added it to config.py imports in app.py

**App still trying to use Supabase**
- Check config.py - make sure `USE_LOCAL_DATABASE = True` is set
- Restart Streamlit (Ctrl+C, then run again)

**Data not saving**
- Check that `data/` folder exists and is writable
- Try deleting data/ folder and restarting

---

## Summary

3 simple steps:
1. ✅ Files created: `local_auth.py` and `local_database.py`
2. ✅ Config change: Add `USE_LOCAL_DATABASE = True` to config.py
3. ✅ Import change: Add conditional imports to app.py

Then the interim version is completely detached from Supabase!

