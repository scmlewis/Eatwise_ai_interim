# EatWise AI - Interim Version

A Streamlit-based nutrition analysis app powered by Azure OpenAI GPT-4 Vision and GPT-4o.

## Features

### 🍽️ Meal Analysis Tab (Hybrid Intelligence)
- Analyze meals by **text description** or **food photo**
- Segmented button interface for easy meal analysis method selection
- **Hybrid Nutrition Analyzer**: Combines GPT detection with USDA database for accuracy
  - GPT-4 Vision detects ingredients and portions
  - Database provides accurate USDA nutrition values (66+ foods)
  - Validation ensures realistic, consistent results
  - **Fixes unrealistic values**: Prevents 0g carbs for vegetable meals
- Instant nutrition breakdown with responsive 3-column grid layout:
  - Calories, Protein, Carbs, Fat, Fiber, Sodium, Sugar (all 7 nutrients)
- Health ratings on a 1-10 scale with visual progress indicator
- Personalized nutrition advice based on your profile and accurate data
- Clear button to reset and analyze another meal

### ⚡ Quick Tips
- Contextual health insights based on detected nutrients
- Tips intelligently compare your meal against personalized nutrition targets
- Includes feedback on:
  - Protein intake (💪 Excellent vs Consider adding more)
  - Fiber content (🥗 Great vs Add more)
  - Sodium levels (🧂 Watch intake alerts)
  - Calorie balance (🔥 Heavy vs Light meal)
  - Macronutrient ratios (⚡ Balance indicators)
- Generated based on your health goal (General wellness, Weight loss, Muscle gain, Energy boost, Heart health)

### 🎯 Nutrition Targets Tab
- Personalized daily nutrition goals calculated from your health goal
- Displays target ranges for all key nutrients
- Requires Age Group profile completion for activation
- Helps you understand daily nutritional targets specific to your goals

### 💡 Coaching Tips Tab
- Tailored nutrition recommendations based on your complete profile
- Health-goal-focused advice
- Considers dietary preferences (Vegetarian, Vegan, Gluten-Free, Low-Carb, Keto)
- Accommodates health conditions (Diabetes, Hypertension, Heart Disease, Celiac, Lactose Intolerance)
- Requires Age Group profile completion for activation

### 📋 Analysis History
- Track your last 5 meal analyses
- Review timestamps, food items, health ratings, and full analyses on demand
- Session-based storage for quick reference

### 👤 User Profile
- **Required fields** (marked with ✓):
  - Age group (18-25, 26-35, 36-45, 46-55, 56+)
  - Health goal (General wellness, Weight loss, Muscle gain, Energy boost, Heart health)
- **Optional fields**:
  - Health conditions (Diabetes, Hypertension, Heart Disease, Celiac, Lactose Intolerance)
  - Dietary preferences (Vegetarian, Vegan, Gluten-Free, Low-Carb, Keto)
- Clear field indicators in sidebar showing which fields are required

## Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI API key
- Streamlit

### Installation

1. Clone the repository
```bash
git clone https://github.com/scmlewis/Eatwise_ai_interim.git
cd Eatwise_ai_interim
```

2. Create virtual environment
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure Azure OpenAI credentials

Create a `.env` file in the root directory:
```
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://hkust.azure-api.net/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2023-05-15
```

5. Run the app
```bash
streamlit run app.py
```

## Deployment

### Streamlit Cloud
1. Push repository to GitHub
2. Connect Streamlit Cloud to your GitHub repository
3. Set secrets in Streamlit Cloud dashboard:
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_DEPLOYMENT`
   - `AZURE_OPENAI_API_VERSION`

## Project Structure

```
Eatwise_ai_interim/
├── app.py                      # Main Streamlit application (1234+ lines)
├── nutrition_analyzer.py       # Hybrid analyzer with LLM + database (468 lines)
├── nutrition_database.py       # USDA nutrition database (466 lines, 66+ foods)
├── config.py                   # Configuration management
├── constants.py                # App constants and settings
├── utils.py                    # Utility functions
├── coaching_assistant.py       # Coaching tips generation
├── gamification.py             # Gamification features
├── recommender.py              # Meal recommendations
├── nutrition_components.py     # Nutrition calculations
├── restaurant_analyzer.py      # Restaurant meal analysis
├── database.py                 # Database utilities
├── auth.py                     # Authentication utilities
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (local dev only)
├── .streamlit/config.toml      # Streamlit settings
├── README.md                   # This file
├── DOCUMENTATION.md            # Full documentation
└── docs/                       # Additional documentation
    ├── PRESENTATION_OUTLINE.md # Presentation slides content
    ├── HYBRID_ANALYZER_ENHANCEMENT.md  # Hybrid system details
    └── [Other guides...]
```

## How It Works

1. **User Profile Setup**: Complete required fields (Age Group, Health Goal) in the sidebar
2. **Meal Analysis**: Choose text or image analysis method
   - For images: Upload a photo and click "Analyze Meal"
   - For text: Describe your meal and click "Analyze Meal"
3. **Instant Feedback**: 
   - View nutrition breakdown in responsive 3-column grid
   - Get quick tips comparing to your personalized targets
   - See health rating with visual progress bar
4. **Personalized Advice**: Access tailored coaching tips based on your profile
5. **Nutrition Planning**: View daily targets in Nutrition Targets tab
6. **Track History**: Review your last 5 analyses anytime

## Technologies

- **Streamlit 1.x**: Modern web framework for interactive data apps
- **Azure OpenAI**: GPT-4o and GPT-4 Vision models for intelligent analysis and detection
- **Python 3.13**: Core runtime environment
- **nutrition_database.py**: USDA-based nutrition database (66+ foods)
- **Pillow (PIL)**: Image processing for food photos
- **python-dotenv**: Environment variable management
- **httpx**: HTTP client for Azure API integration

## Features Highlights

✨ **Hybrid Nutrition Analyzer**: Combines GPT detection with USDA database for accurate, consistent results

📊 **Smart Nutrition Extraction**: Automatically detects all 7 nutrients from meal descriptions and photos

💾 **Comprehensive Database**: 66+ USDA foods with accurate nutritional values and portion conversion

🔍 **Validation System**: Catches and corrects impossible nutrition values (e.g., vegetables with 0g carbs)

📱 **Responsive Design**: Works seamlessly on desktop and mobile browsers

🎨 **Modern UI**: Clean, gradient-based design with intuitive navigation using tabs

🎯 **Goal-Driven**: Personalized recommendations based on health goals (wellness, weight loss, muscle gain, energy, heart health)

⚡ **Quick Insights**: Instant contextual tips without waiting for full analysis

🔐 **Secure**: Credentials stored in environment variables, never hardcoded

## Performance Notes

- First meal analysis may take 10-15 seconds (Azure OpenAI processing)
- Subsequent analyses typically complete in 5-10 seconds
- Image analysis uses GPT-4 Vision (slightly slower but more accurate)
- Text analysis uses GPT-4o (faster processing)

## License

MIT License

## Author

Built as an interim solution for personalized nutrition analysis and coaching.

---

**Last Updated**: November 29, 2025
**Version**: 2.1 (Hybrid Nutrition Analyzer - Production Ready)
