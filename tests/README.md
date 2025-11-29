# Tests & Validation (`tests/`)

This folder contains test scripts and validation tools for the EatWise nutrition analyzer.

## Test Files

### `test_hybrid_analyzer.py`
Comprehensive demonstration of the hybrid nutrition analyzer system.

**Purpose:** Shows improvement of LLM-only approach vs hybrid approach

**Test Cases:**
1. **Grilled Chicken with Roasted Vegetables** - Demonstrates accurate nutrition calculation
2. **Various meal compositions** - Tests database lookup and portion conversion
3. **Nutritional validation** - Confirms realistic values and consistency

**Run:** 
```bash
cd tests
python test_hybrid_analyzer.py
```

**Output:** 
Shows side-by-side comparison of:
- LLM-only estimates (old approach)
- Database-backed values (new hybrid approach)
- Validation results

### `validate_results.py`
Validates expected nutrition values for standard meal combinations.

**Purpose:** Compare expected vs actual nutrition values from the analyzer

**Functionality:**
- Reconstructs meals from ingredients
- Calculates expected nutrition using the database
- Compares with actual app output
- Validates consistency

**Run:**
```bash
cd tests
python validate_results.py
```

**Output:**
Detailed breakdown showing:
- Individual ingredient nutrition
- Total calculated values
- Comparison with screenshot values
- Validation status (✓ or ✗)

### `validate_actual_meal.py`
Validates the specific meal shown in the app screenshot.

**Purpose:** Ensures the hybrid analyzer is working correctly with real data

**Functionality:**
- Analyzes the egg soup with grilled chicken from screenshot
- Verifies all nutrients are displaying
- Confirms carbs and fiber show realistic values (not 0g)
- Checks logicalconsistency

**Run:**
```bash
cd tests
python validate_actual_meal.py
```

**Output:**
Validation report showing:
- Expected nutrition values (from database)
- Actual values (from screenshot)
- Status: VALIDATION SUCCESSFUL
- Key improvements (0g carbs → 8.9g, 1g fiber → 6.8g)

## Import System

All test files use Python path manipulation to import from `src/`:

```python
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nutrition_database import get_nutrition_for_portion
from nutrition_analyzer import NutritionAnalyzer
```

This allows tests to run from any directory while maintaining clean imports.

## Running All Tests

From the repository root:

```bash
# Run individual tests
python tests/test_hybrid_analyzer.py
python tests/validate_results.py
python tests/validate_actual_meal.py

# Or run specific validation
python -m tests.test_hybrid_analyzer
```

## Test Coverage

**System Tested:**
- ✓ Database lookup accuracy
- ✓ Portion conversion (g, oz, cup, tbsp, tsp)
- ✓ Mixed meal calculation
- ✓ Validation logic (carbs, fiber consistency)
- ✓ Fallback estimation for unknown foods
- ✓ Before/after comparison (LLM-only vs hybrid)

**Validation Results:**
- ✓ All nutrients display (not just calories)
- ✓ Carbs showing realistic values (8.9g, not 0g)
- ✓ Fiber showing realistic values (6.8g, not 1g)
- ✓ No impossible nutritional combinations
- ✓ Values are logically consistent

## Dependencies

These tests require:
- `nutrition_database.py` from `src/`
- Standard library modules (`sys`, `pathlib`)
- (Optional) `nutrition_analyzer.py` for full system tests

## Performance Baseline

Expected execution times:

| Test | Time | Notes |
|------|------|-------|
| `test_hybrid_analyzer.py` | ~1 second | All local calculations |
| `validate_results.py` | ~1 second | No API calls |
| `validate_actual_meal.py` | ~1 second | No API calls |
| Full test suite | ~3 seconds | Pure database operations |

## Troubleshooting

### Import Errors
If you see "ModuleNotFoundError: No module named 'nutrition_database'":
- Ensure you're running from the project root or `tests/` directory
- Check that `src/` folder exists
- Verify `src/__init__.py` exists (or create if needed)

### Validation Failures
If tests fail:
1. Check that `nutrition_database.py` is in `src/`
2. Verify database has 66+ foods defined
3. Run with verbose output to see exact values
4. Check console output for specific assertion failures

---

**Last Updated:** November 30, 2025  
**Status:** All Tests Passing ✓
