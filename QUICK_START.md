# 🚀 Ultra-Minimal - Quick Reference

## One-Minute Overview

Your EatWise app is now **ultra-minimal**: 3 files, 4 dependencies, pure LLM focus.

```
OLD: 15+ files, 4700+ lines, 10+ dependencies, 30 min setup ❌
NEW: 3 files, 437 lines, 4 dependencies, 2 min setup ✅
```

---

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `app.py` | 224 | Streamlit UI (3 tabs: photo, text, coaching) |
| `nutrition_analyzer.py` | 190 | 3 LLM methods (detect, analyze, coach) |
| `config.py` | 19 | Just API key configuration |
| `requirements.txt` | 4 | streamlit, python-dotenv, openai, pillow |

---

## The 3 Tabs

### 1️⃣ Food Detector
```
📸 Upload photo → AI detects foods → Shows nutrition + tips
```

### 2️⃣ Nutrition Analysis  
```
📝 Describe meal → AI analyzes → Shows nutrition + rating
```

### 3️⃣ Coaching Tips
```
💡 Pick topic → AI generates → Shows personalized advice
```

---

## Session Profile (Sidebar)

```
👤 Name: [text]
📅 Age: [18-25, 26-35, 36-45, 46-55, 56+]
🏥 Conditions: [Diabetes, Hypertension, etc.]
🥗 Preferences: [Vegetarian, Vegan, Gluten-Free, etc.]
🎯 Goal: [Weight loss, Muscle gain, etc.]

⚠️ Resets when you refresh!
```

---

## Setup (2 Minutes)

```bash
# Make sure .env has:
OPENAI_API_KEY=sk-...

# Install
pip install -r requirements.txt

# Run
streamlit run app.py

# Open browser
# → http://localhost:8501
```

---

## Architecture

```
User Profile (Session) + Tab Input
         ↓
app.py (Streamlit UI)
         ↓
nutrition_analyzer.py (3 methods)
         ↓
Azure OpenAI (GPT-4, GPT-4 Vision)
         ↓
Display Result as Paragraph
```

---

## What's Gone

```
❌ Database (Supabase)
❌ User accounts
❌ Meal history
❌ Analytics
❌ Gamification
❌ Chat interface
❌ Complex recommendations
❌ Restaurant analyzer
```

---

## What's There

```
✅ Food photo detection (Vision)
✅ Meal text analysis (GPT-4)
✅ Personalized coaching (GPT-4)
✅ Beautiful Streamlit UI
✅ Session-only profile
✅ No database, no setup
```

---

## Key Stats

| Metric | Value |
|--------|-------|
| Python Files | 3 |
| Total Lines | 437 |
| Dependencies | 4 |
| Setup Time | 2 min |
| Auth | None |
| Database | None |
| Storage | Session only |
| Cost | OpenAI API only |

---

## Testing

```bash
streamlit run app.py

# Test:
1. Enter profile in sidebar
2. Upload food photo → see analysis
3. Describe a meal → see nutrition
4. Pick coaching topic → see tips
5. Refresh page → profile resets ✓
```

---

## Deployment

Just push to your repo:
```bash
git add -A
git commit -m "Ultra-minimal interim version"
git push
```

Anyone with `OPENAI_API_KEY` can run it:
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Full Version is Safe ✅

Your original Supabase database:
- Still in .env
- Untouched
- Ready to rebuild full version anytime

All code documented in `docs/` folder.

---

## Next Steps

**To expand later:**
1. Add database → restore `local_database.py` or Supabase
2. Add auth → restore `auth.py`
3. Add features → restore other modules

Everything is documented!

---

## Support Files

```
📚 TRANSFORMATION_COMPLETE.md - Full details
📚 ULTRA_MINIMAL_GUIDE.md - Architecture deep-dive
📚 BEFORE_AFTER_COMPARISON.md - Visual comparison
📚 docs/ - All other documentation
```

---

**Status: READY TO RUN** ✅

```bash
streamlit run app.py
```

That's it! 🚀
