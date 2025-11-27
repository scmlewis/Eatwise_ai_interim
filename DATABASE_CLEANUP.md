# Database Cleanup Guide - EatWise Demake

## Overview

This guide shows you **exactly which database tables, columns, and functions to remove** when demaking EatWise. You have two options:

### Option 1: Keep Database Schema (Recommended - Easiest)
- Keep database tables unchanged
- Gamification data remains in database but unused
- App code ignores those tables
- **Pros:** No SQL, no data loss, easy rollback
- **Cons:** Slight database overhead

### Option 2: Clean Database Schema (Complete Cleanup)
- Remove all gamification-related tables/columns
- Run SQL migrations to drop unused tables
- Smaller, cleaner database
- **Pros:** Professional, minimal overhead
- **Cons:** SQL required, harder to rollback

---

## Option 1: Code-Only Cleanup (Recommended)

### Step 1: Remove Functions from `database.py`

Remove these **entire function blocks** from `database.py`:

#### GAMIFICATION: XP & POINTS Section (~40 lines)
```python
# Remove these functions entirely:
- add_xp()
- get_user_level()
- get_user_xp_progress()
```

#### GAMIFICATION: DAILY CHALLENGES Section (~50 lines)
```python
# Remove these functions entirely:
- get_daily_challenges()
- create_daily_challenges()
- update_challenge_progress()
- complete_challenge()
```

#### GAMIFICATION: WEEKLY GOALS Section (~50 lines)
```python
# Remove these functions entirely:
- get_weekly_goals()
- create_weekly_goals()
- increment_weekly_days_completed()
```

#### WATER TRACKING Section (~40 lines)
```python
# Remove these functions entirely:
- log_water()
- get_daily_water_intake()
```

#### BADGES & GAMIFICATION Section (~25 lines)
```python
# Remove these functions entirely:
- update_badges()
- add_badge()
```

### Step 2: Simplify `health_profiles` Operations

The `health_profiles` table still exists, but remove gamification-specific fields from create/update:

**In `create_health_profile()` - Update valid_fields:**
```python
# OLD:
valid_fields = {
    "user_id", "full_name", "age_group", "gender", "timezone", 
    "health_conditions", "dietary_preferences", "health_goal"
}

# NEW (already done - no change needed):
valid_fields = {
    "user_id", "full_name", "age_group", "gender", "timezone", 
    "health_conditions", "dietary_preferences", "health_goal"
}
```

**In `update_health_profile()` - Already clean:**
- No changes needed - already excludes XP fields

### Step 3: Impact Summary

**Affected Parts of App:**
- Dashboard won't show XP/level/challenges
- Analytics won't show badges
- Database table still has data but won't be accessed
- All meal logging/nutrition tracking works unchanged

**No Database Changes Needed**

---

## Option 2: Complete Database Cleanup

### Prerequisites
- Access to Supabase SQL editor
- Backup of database (optional but recommended)

### Step 1: Remove Tables via SQL

Run these SQL commands in Supabase SQL editor:

```sql
-- ==================== DROP GAMIFICATION TABLES ====================

-- Drop daily_challenges table
DROP TABLE IF EXISTS daily_challenges CASCADE;

-- Drop weekly_goals table
DROP TABLE IF EXISTS weekly_goals CASCADE;

-- Drop water_intake table
DROP TABLE IF EXISTS water_intake CASCADE;
```

### Step 2: Remove Columns from health_profiles

Run these in Supabase SQL editor:

```sql
-- ==================== REMOVE GAMIFICATION COLUMNS ====================

-- Remove XP tracking columns
ALTER TABLE health_profiles DROP COLUMN IF EXISTS total_xp CASCADE;
ALTER TABLE health_profiles DROP COLUMN IF EXISTS timezone CASCADE;
ALTER TABLE health_profiles DROP COLUMN IF EXISTS badges_earned CASCADE;
ALTER TABLE health_profiles DROP COLUMN IF EXISTS gender CASCADE;

-- Remove old water goal column if exists
ALTER TABLE health_profiles DROP COLUMN IF EXISTS water_goal_glasses CASCADE;
```

### Step 3: Drop Indexes (Automatic with Table Drop)

When you drop the tables above, associated indexes are automatically removed. But if you want to verify:

```sql
-- These indexes are automatically dropped when tables are dropped
-- idx_water_intake_user_id
-- idx_water_intake_date
-- idx_daily_challenges_user_id
-- idx_daily_challenges_date
-- idx_weekly_goals_user_id
-- idx_weekly_goals_week_start
```

### Step 4: Drop Unused Policies (Automatic with Table Drop)

When tables are dropped, their RLS policies are automatically removed.

### Step 5: Code Changes (Same as Option 1)

Still remove all the functions from `database.py` as shown in Option 1, Steps 1-2.

---

## Complete Function Removal List (Option 1)

Here's a checklist of ALL functions to remove from `database.py`:

**Section: WATER TRACKING**
- [ ] `log_water()` - ~25 lines
- [ ] `get_daily_water_intake()` - ~15 lines

**Section: BADGES & GAMIFICATION**
- [ ] `update_badges()` - ~10 lines
- [ ] `add_badge()` - ~10 lines

**Section: GAMIFICATION: XP & POINTS**
- [ ] `add_xp()` - ~12 lines
- [ ] `get_user_level()` - ~8 lines
- [ ] `get_user_xp_progress()` - ~18 lines

**Section: GAMIFICATION: DAILY CHALLENGES**
- [ ] `get_daily_challenges()` - ~10 lines
- [ ] `create_daily_challenges()` - ~25 lines
- [ ] `update_challenge_progress()` - ~10 lines
- [ ] `complete_challenge()` - ~20 lines

**Section: GAMIFICATION: WEEKLY GOALS**
- [ ] `get_weekly_goals()` - ~10 lines
- [ ] `create_weekly_goals()` - ~20 lines
- [ ] `increment_weekly_days_completed()` - ~20 lines

**Total: ~183 lines of code to remove**

**Functions to KEEP:**
- ✓ All HEALTH PROFILE functions
- ✓ All MEAL LOGGING functions
- ✓ All MEAL HISTORY & TRENDS functions
- ✓ All PREFERENCES & HISTORY functions

---

## Database State After Cleanup

### Option 1 (Keep Schema):
```
Database Tables (Unchanged):
├── users ✓ Used
├── health_profiles ✓ Used (but without XP/badges access)
├── meals ✓ Used
├── food_history ✓ Used
├── water_intake ✗ Unused (but exists)
├── daily_challenges ✗ Unused (but exists)
└── weekly_goals ✗ Unused (but exists)

Columns in health_profiles:
├── id ✓
├── user_id ✓
├── full_name ✓
├── age_group ✓
├── health_conditions ✓
├── dietary_preferences ✓
├── health_goal ✓
├── created_at ✓
├── updated_at ✓
├── total_xp ✗ (unused)
├── timezone ✗ (unused)
└── badges_earned ✗ (unused)
```

### Option 2 (Clean Schema):
```
Database Tables (Cleaned):
├── users ✓ Used
├── health_profiles ✓ Used
├── meals ✓ Used
└── food_history ✓ Used

Columns in health_profiles (Cleaned):
├── id ✓
├── user_id ✓
├── full_name ✓
├── age_group ✓
├── health_conditions ✓
├── dietary_preferences ✓
├── health_goal ✓
├── created_at ✓
└── updated_at ✓
```

---

## Step-by-Step Implementation

### For Option 1 (Recommended):

**Time:** ~30 minutes
**Complexity:** Low (Python only, no SQL)

1. Open `database.py`
2. Find each section header (WATER TRACKING, BADGES & GAMIFICATION, XP & POINTS, DAILY CHALLENGES, WEEKLY GOALS)
3. Delete the entire section (including the comment header)
4. Save file
5. Test app runs without errors

### For Option 2:

**Time:** ~15 minutes
**Complexity:** Medium (SQL + Python)

1. Go to Supabase SQL Editor
2. Run the DROP TABLE commands
3. Run the ALTER TABLE DROP COLUMN commands
4. Wait for queries to complete
5. Verify tables are dropped in Table Browser
6. Follow Option 1 code removal steps
7. Test app runs without errors

---

## Testing After Cleanup

### Create Simple Test Script

Create `test_database.py`:

```python
from database import DatabaseManager
from datetime import date
import uuid

# Test that core functions still work
db = DatabaseManager()
test_user_id = str(uuid.uuid4())

# Test health profile operations (should work)
profile = {
    "full_name": "Test User",
    "age_group": "26-35",
    "health_conditions": ["None"],
    "dietary_preferences": ["Vegetarian"],
    "health_goal": "Weight Loss"
}

# This should work fine
print("✓ Testing health profile creation...")
result = db.create_health_profile(test_user_id, profile)
print(f"Result: {result}")

# Get profile back
fetched = db.get_health_profile(test_user_id)
print(f"✓ Fetched profile: {fetched}")

# Test meal operations (should work)
print("\n✓ Testing meal operations...")
meal = {
    "user_id": test_user_id,
    "meal_name": "Test Meal",
    "meal_type": "breakfast",
    "nutrition": {"calories": 500, "protein": 25}
}
result = db.log_meal(meal)
print(f"Meal logged: {result}")

# These functions should now fail (or not exist)
print("\n✓ Testing removed functions...")
try:
    db.add_xp(test_user_id, 100)
    print("WARNING: add_xp still exists!")
except AttributeError:
    print("✓ add_xp successfully removed")

try:
    db.log_water(test_user_id, 8)
    print("WARNING: log_water still exists!")
except AttributeError:
    print("✓ log_water successfully removed")

print("\n✓ All tests passed!")
```

Run with:
```bash
python test_database.py
```

---

## Troubleshooting

### If app crashes after cleanup:

**Error:** `AttributeError: 'DatabaseManager' has no attribute 'add_xp'`
- **Cause:** Function still being called somewhere in app.py
- **Fix:** Search app.py for the function name and remove the call

**Error:** `Error fetching health profile: ...`
- **Cause:** Database structure mismatch
- **Fix:** Check that you didn't remove health profile functions (only gamification ones)

**Error:** `Table 'daily_challenges' does not exist`
- **Cause:** Trying to access dropped table
- **Fix:** Remove all code that references that table (already done if you remove app.py functions)

---

## Recommended Approach

### Start with Option 1
1. Remove functions from `database.py` (safer, reversible)
2. Remove code from `app.py` (as per DEMAKE_STRATEGY.md)
3. Test thoroughly
4. If everything works → Option 2 is optional

### Then Optional: Option 2
5. Run SQL to drop tables (clean up database)
6. Verify app still works (it should, since code doesn't use those tables)

---

## Summary Table

| Task | Option 1 | Option 2 |
|------|----------|----------|
| Remove functions from database.py | Required | Required |
| Run SQL in Supabase | No | Yes |
| Database Size | Slightly larger | Minimal |
| Reversibility | Easy (restore from git) | Medium (need SQL restore) |
| Data Loss | No (unused tables remain) | Yes (tables dropped) |
| Recommended | ✓ Start here | ✓ After confirming Option 1 works |

---

## Files Affected

### Code Changes:
- `database.py` - Remove ~9 function blocks (~180 lines)

### SQL Changes (Option 2 only):
- Run in Supabase SQL editor
- No files to modify

### No Changes Needed:
- `app.py` - Already handled by removing functions from database.py
- `config.py` - No database-specific config
- Other modules - No database schema dependencies

---

## Next Steps

1. **Choose Option 1 or 2** based on preference
2. **For Option 1:** Remove functions from `database.py` (do this first regardless)
3. **For Option 2:** Run SQL commands in Supabase after Option 1
4. **Test:** Run app to ensure no errors
5. **Verify:** Check that core nutrition features still work

Would you like me to help with removing specific functions or running the SQL commands?

