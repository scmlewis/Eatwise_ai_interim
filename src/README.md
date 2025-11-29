# Source Modules (`src/`)

This folder contains the core Python modules for the EatWise nutrition analysis system.

## Module Overview

### `config.py`
Configuration management module that loads environment variables and settings.

**Key Functions:**
- Loads Azure OpenAI API credentials
- Defines app constants (APP_NAME, version info)
- Exports: OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION

### `nutrition_analyzer.py`
Hybrid nutrition analysis engine combining GPT detection with database values.

**Key Class:** `NutritionAnalyzer`

**Main Methods:**
- `detect_food_from_image()` - Analyzes food photo via GPT-4 Vision
- `analyze_text_meal()` - Analyzes text meal description via GPT-4o
- `_calculate_hybrid_nutrition()` - Combines database lookup with GPT intelligence

**Features:**
- Hybrid approach: LLM detection + USDA database calculation
- Nutrition validation to catch unrealistic values
- Personalized analysis based on user profile
- Quick tips generation

### `nutrition_database.py`
USDA-based nutrition database with 66+ common foods.

**Key Functions:**
- `find_food_matches(food_name)` - Fuzzy search for foods
- `get_nutrition_for_portion(name, quantity, unit)` - Calculate nutrition for specific portions
- `validate_nutrition_data(nutrition_dict)` - Verify logical consistency

**Database Contents:**
- Proteins: 11 entries (chicken, beef, fish, etc.)
- Vegetables: 15 entries
- Fruits: 8 entries
- Grains: 7 entries
- Legumes: 6 entries
- Dairy: 6 entries
- Oils & Condiments: 7+ entries

**Data Source:** USDA Nutrition Database (per-100g standardized)

## Usage

These modules are imported by `app.py` via:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nutrition_analyzer import NutritionAnalyzer
from config import APP_NAME, OPENAI_API_KEY, ...
```

## Module Dependencies

- `openai` - Azure OpenAI API client
- `python-dotenv` - Environment variable loading
- `requests` - HTTP client for API calls
- Standard library: `os`, `json`, `re`, `datetime`

## Performance

- Nutrition database lookups: <10ms
- Food detection via GPT-4 Vision: 5-10 seconds
- Text analysis via GPT-4o: 2-5 seconds
- Full analysis pipeline: 10-15 seconds

## Extending the Database

To add more foods to `nutrition_database.py`:

```python
NUTRITION_DATABASE["new food name"] = {
    "calories": 150,
    "protein": 20,
    "carbs": 5,
    "fat": 3,
    "fiber": 2,
    "sodium": 100,
    "sugar": 1,
    "category": "protein",
    "common_portions": {"g": 100}
}
```

---

**Last Updated:** November 30, 2025
