# EatWise AI - Interim Version

A Streamlit-based nutrition analysis app powered by Azure OpenAI GPT-4 Vision and GPT-4o.

## Features

🍽️ **Meal Analysis**
- Analyze meals by **text description** or **food photo**
- Get instant nutrition breakdown (Calories, Protein, Carbs, Fat, Fiber, Sodium, Sugar)
- Receive health ratings (1-10 scale)
- Get personalized nutrition advice

💡 **Personalized Coaching**
- Tailored nutrition tips based on your profile
- Health-goal-focused recommendations
- Dietary preference considerations
- Health condition accommodations

📋 **Analysis History**
- Track your last 5 meal analyses
- Review nutritional insights on demand

👤 **User Profile**
- Age group selection
- Health conditions tracking
- Dietary preferences
- Health goals

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
source venv/Scripts/activate  # On Windows
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
Set secrets in Streamlit Cloud dashboard:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

## Project Structure

```
Eatwise_ai_interim/
├── app.py                    # Main Streamlit application
├── nutrition_analyzer.py     # Azure OpenAI integration
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (local dev)
├── .streamlit/config.toml    # Streamlit settings
└── README.md                 # This file
```

## Technologies

- **Streamlit**: Web framework for interactive UI
- **Azure OpenAI**: GPT-4 Vision and GPT-4o models
- **Python 3.13**: Core runtime

## License

MIT License

## Author

Built as an interim solution for nutrition analysis.
