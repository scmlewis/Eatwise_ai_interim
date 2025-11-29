"""
EatWise AI - Hybrid Nutrition Analyzer
LLM-powered ingredient detection + Database-backed nutrition values
"""

import json
import base64
import re
from typing import Dict, Optional, Tuple
from openai import AzureOpenAI
import httpx
from nutrition_database import find_food_matches, get_nutrition_for_portion, validate_nutrition_data


class NutritionAnalyzer:
    """Analyzes food using Azure OpenAI GPT-4 Vision and GPT-4 (HKUST endpoint)"""
    
    def __init__(self, api_key: str, endpoint: str = None, deployment: str = None, api_version: str = None):
        """Initialize with Azure OpenAI API key and endpoint
        
        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint (defaults to HKUST)
            deployment: Deployment name (defaults to gpt-4o)
            api_version: API version (defaults to 2024-05-01-preview)
        """
        if not api_key:
            raise ValueError("Azure OpenAI API key is required. Please set AZURE_OPENAI_API_KEY in your .env file")
        
        self.api_key = api_key
        self.endpoint = endpoint or "https://hkust.azure-api.net/"
        self.deployment = deployment or "gpt-4o"
        self.api_version = api_version or "2023-05-15"
        
        # Ensure endpoint ends with /
        if self.endpoint and not self.endpoint.endswith("/"):
            self.endpoint += "/"
        
        try:
            # Create a custom httpx client with proper configuration
            http_client = httpx.Client(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint,
                http_client=http_client
            )
        except Exception as e:
            error_msg = str(e)
            # Print detailed debug info to logs
            import sys
            print(f"DEBUG: Endpoint: {self.endpoint}", file=sys.stderr)
            print(f"DEBUG: API Version: {self.api_version}", file=sys.stderr)
            print(f"DEBUG: Deployment: {self.deployment}", file=sys.stderr)
            print(f"DEBUG: API Key length: {len(api_key) if api_key else 0}", file=sys.stderr)
            print(f"DEBUG: Error: {error_msg}", file=sys.stderr)
            
            # Provide more specific error messages
            if "invalid_request_error" in error_msg.lower() or "authentication" in error_msg.lower():
                raise RuntimeError(f"Authentication failed. Please verify your AZURE_OPENAI_API_KEY is correct. Error: {error_msg}")
            elif "endpoint" in error_msg.lower():
                raise RuntimeError(f"Invalid endpoint. Configured endpoint: {self.endpoint}. Error: {error_msg}")
            elif "api_version" in error_msg.lower() or "version" in error_msg.lower():
                raise RuntimeError(f"Invalid API version '{self.api_version}'. Error: {error_msg}")
            else:
                raise RuntimeError(f"Failed to initialize Azure OpenAI client. Endpoint: {self.endpoint}, API Version: {self.api_version}. Error: {error_msg}")
    
    def detect_food_from_image(self, image_data: bytes, profile: Dict) -> str:
        """
        Detect food from image and provide hybrid nutrition analysis.
        Uses LLM to detect ingredients, then database for accurate nutrition values.
        
        Args:
            image_data: Image bytes
            profile: User profile (name, age_group, health_conditions, dietary_preferences, health_goal)
            
        Returns:
            Formatted markdown string with analysis
        """
        try:
            # Convert image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Step 1: Use GPT-4 Vision to detect food items and portions
            detection_prompt = """Analyze this food image and extract:

1. **Food Items**: List each food item with estimated portion (e.g., "150g chicken breast", "1 cup broccoli", "2 tbsp olive oil")
2. **Preparation**: Note if grilled, fried, roasted, raw, etc.

Format as JSON:
{
    "items": [
        {"name": "chicken breast", "quantity": 150, "unit": "g", "preparation": "grilled"},
        {"name": "broccoli", "quantity": 1, "unit": "cup", "preparation": "roasted"}
    ],
    "meal_description": "brief description of the meal"
}"""
            
            detection_response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": detection_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent detection
                max_tokens=400
            )
            
            # Step 2: Parse detected items and get nutrition from database
            try:
                detection_text = detection_response.choices[0].message.content
                # Extract JSON from response
                json_match = re.search(r'\{[\s\S]*\}', detection_text)
                if json_match:
                    detection_data = json.loads(json_match.group())
                else:
                    detection_data = {"items": [], "meal_description": ""}
            except:
                detection_data = {"items": [], "meal_description": ""}
            
            # Step 3: Calculate nutrition using hybrid approach
            total_nutrition = self._calculate_hybrid_nutrition(detection_data.get("items", []))
            meal_description = detection_data.get("meal_description", "")
            
            # Step 4: Generate personalized analysis with accurate nutrition values
            context = self._build_profile_context(profile)
            
            analysis_prompt = f"""Based on this meal analysis, provide comprehensive health guidance:

Meal: {meal_description}
Nutrition Summary:
- Calories: {total_nutrition['calories']} cal
- Protein: {total_nutrition['protein']}g
- Carbs: {total_nutrition['carbs']}g
- Fat: {total_nutrition['fat']}g
- Fiber: {total_nutrition['fiber']}g
- Sodium: {total_nutrition['sodium']}mg
- Sugar: {total_nutrition['sugar']}g

User Profile:
{context}

Provide a comprehensive analysis including:
1. **Your Meal**: Description and food items
2. **Nutrition Analysis**: Interpretation of the values above
3. **Health Rating**: Rate this meal 1-10 for overall healthiness
4. **Personalized Advice**: Tips specific to their health goal and conditions

Format as readable paragraphs with a clear "Health Rating: X/10" line."""
            
            final_response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a nutrition expert. Provide evidence-based analysis using the provided nutritional data. Format your response as clear paragraphs."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return final_response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"Image analysis error: {str(e)}")
    
    def analyze_text_meal(self, meal_description: str, profile: Dict) -> str:
        """
        Analyze meal from text description using hybrid approach.
        Extracts ingredients and portions, then uses database for accurate nutrition.
        
        Args:
            meal_description: Text description of the meal
            profile: User profile (name, age_group, health_conditions, dietary_preferences, health_goal)
            
        Returns:
            Formatted markdown string with analysis
        """
        try:
            # Step 1: Use GPT to extract structured ingredient data
            extraction_prompt = f"""Extract ingredients and portions from this meal description and format as JSON.

Meal: {meal_description}

For each ingredient, estimate the portion size. Format as:
{{
    "items": [
        {{"name": "ingredient", "quantity": 100, "unit": "g", "preparation": "method"}},
        {{"name": "ingredient2", "quantity": 1, "unit": "cup", "preparation": "method"}}
    ],
    "meal_description": "brief summary"
}}

Common units: g, oz, cup, tbsp, tsp, slice, medium, small, large"""
            
            extraction_response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract structured ingredient data from meal descriptions. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": extraction_prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistent JSON
                max_tokens=500
            )
            
            # Step 2: Parse extraction and get hybrid nutrition
            try:
                extraction_text = extraction_response.choices[0].message.content
                json_match = re.search(r'\{[\s\S]*\}', extraction_text)
                if json_match:
                    extraction_data = json.loads(json_match.group())
                else:
                    extraction_data = {"items": [], "meal_description": meal_description}
            except:
                extraction_data = {"items": [], "meal_description": meal_description}
            
            # Step 3: Calculate nutrition using hybrid database approach
            total_nutrition = self._calculate_hybrid_nutrition(extraction_data.get("items", []))
            
            # Step 4: Generate personalized analysis
            context = self._build_profile_context(profile)
            
            analysis_prompt = f"""Based on this meal analysis, provide comprehensive health guidance:

Meal: {extraction_data.get('meal_description', meal_description)}
Nutrition Summary:
- Calories: {total_nutrition['calories']} cal
- Protein: {total_nutrition['protein']}g
- Carbs: {total_nutrition['carbs']}g
- Fat: {total_nutrition['fat']}g
- Fiber: {total_nutrition['fiber']}g
- Sodium: {total_nutrition['sodium']}mg
- Sugar: {total_nutrition['sugar']}g

User Profile:
{context}

Provide a comprehensive analysis including:
1. **Your Meal**: Description of the food items
2. **Nutrition Analysis**: Interpretation of the values
3. **Health Rating**: Rate this meal 1-10 for overall healthiness
4. **Personalized Recommendations**: Tips specific to their health goal and conditions

Format as readable paragraphs with a clear "Health Rating: X/10" line."""
            
            final_response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a nutrition expert. Provide evidence-based analysis using the provided nutritional data."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return final_response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"Meal analysis error: {str(e)}")
    
    def get_personalized_coaching(self, topic: str, profile: Dict) -> str:
        """
        Generate personalized nutrition coaching tips.
        
        Args:
            topic: Coaching topic (e.g., "Daily nutrition tips", "How to improve my diet for my health goal")
            profile: User profile (name, age_group, health_conditions, dietary_preferences, health_goal)
            
        Returns:
            Formatted markdown string with coaching tips
        """
        try:
            # Build personalization context
            context = self._build_profile_context(profile)
            
            prompt = f"""Provide personalized nutrition coaching on this topic: {topic}

User Profile:
{context}

Generate practical, actionable advice in paragraph format. Focus on:
- Specific recommendations for their health goal
- Consideration of their health conditions
- Respect for their dietary preferences
- Practical, easy-to-implement tips

Make it conversational and encouraging."""
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a compassionate and knowledgeable nutrition coach. Provide personalized, actionable advice in an encouraging tone."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"Coaching generation error: {str(e)}")
    
    def _calculate_hybrid_nutrition(self, items: list) -> Dict:
        """
        Calculate total nutrition using hybrid database + estimation approach.
        Uses nutrition database for known foods, estimation for unknowns.
        
        Args:
            items: List of food items with quantity and unit
            
        Returns:
            Dictionary with total nutrition values
        """
        total = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0,
            "sodium": 0,
            "sugar": 0
        }
        
        for item in items:
            food_name = item.get("name", "").lower()
            quantity = item.get("quantity", 100)
            unit = item.get("unit", "g")
            
            # Try to find in database
            matches = find_food_matches(food_name)
            
            if matches:
                # Use database nutrition values
                nutrition = get_nutrition_for_portion(food_name, quantity, unit)
                if nutrition:
                    for nutrient in total:
                        total[nutrient] += nutrition.get(nutrient, 0)
            else:
                # Fallback: estimate based on food category
                estimated = self._estimate_nutrition(food_name, quantity, unit)
                for nutrient in total:
                    total[nutrient] += estimated.get(nutrient, 0)
        
        # Validate and correct total nutrition
        total = validate_nutrition_data(total)
        
        # Round all values
        for nutrient in total:
            total[nutrient] = round(total[nutrient], 1)
        
        return total
    
    def _estimate_nutrition(self, food_name: str, quantity: float, unit: str) -> Dict:
        """
        Estimate nutrition for foods not in database using heuristics.
        
        Args:
            food_name: Name of the food
            quantity: Amount
            unit: Unit of measurement
            
        Returns:
            Estimated nutrition dictionary
        """
        # Base estimates per 100g based on food categories
        estimates = {
            "meat": {"calories": 200, "protein": 26, "carbs": 0, "fat": 10, "fiber": 0, "sodium": 80, "sugar": 0},
            "fish": {"calories": 150, "protein": 20, "carbs": 0, "fat": 7, "fiber": 0, "sodium": 50, "sugar": 0},
            "vegetable": {"calories": 40, "protein": 2, "carbs": 8, "fat": 0.3, "fiber": 2, "sodium": 30, "sugar": 2},
            "fruit": {"calories": 60, "protein": 0.7, "carbs": 15, "fat": 0.2, "fiber": 2, "sodium": 5, "sugar": 10},
            "grain": {"calories": 130, "protein": 4, "carbs": 28, "fat": 1, "fiber": 2, "sodium": 5, "sugar": 0.5},
            "legume": {"calories": 140, "protein": 8, "carbs": 25, "fat": 1, "fiber": 6, "sodium": 10, "sugar": 1},
            "dairy": {"calories": 150, "protein": 8, "carbs": 5, "fat": 8, "fiber": 0, "sodium": 200, "sugar": 4},
            "oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100, "fiber": 0, "sodium": 0, "sugar": 0},
        }
        
        # Determine category based on food name keywords
        category = "vegetable"  # Default
        food_lower = food_name.lower()
        
        if any(x in food_lower for x in ["chicken", "beef", "pork", "meat", "turkey", "lamb", "steak"]):
            category = "meat"
        elif any(x in food_lower for x in ["fish", "salmon", "tuna", "cod", "shrimp", "seafood"]):
            category = "fish"
        elif any(x in food_lower for x in ["apple", "banana", "orange", "fruit", "berry", "grape"]):
            category = "fruit"
        elif any(x in food_lower for x in ["rice", "bread", "pasta", "grain", "cereal", "oat"]):
            category = "grain"
        elif any(x in food_lower for x in ["bean", "lentil", "chickpea", "legume", "pea"]):
            category = "legume"
        elif any(x in food_lower for x in ["cheese", "milk", "yogurt", "butter", "dairy"]):
            category = "dairy"
        elif any(x in food_lower for x in ["oil", "fat", "butter", "mayo"]):
            category = "oil"
        
        # Get base estimate
        base_nutrition = estimates[category].copy()
        
        # Convert quantity to grams
        from nutrition_database import PORTION_MULTIPLIERS
        unit_lower = unit.lower().strip()
        multiplier = PORTION_MULTIPLIERS.get(unit_lower, 1/100)
        grams = quantity * multiplier * 100
        
        # Apply portion size
        portion_multiplier = grams / 100
        result = {}
        for nutrient, value in base_nutrition.items():
            result[nutrient] = round(value * portion_multiplier, 1)
        
        return result
    
    def _build_profile_context(self, profile: Dict) -> str:
        """Build readable profile context for prompts"""
        lines = []
        
        if profile.get("age_group") and profile["age_group"] != "Not selected":
            lines.append(f"- Age Group: {profile['age_group']}")
        
        if profile.get("health_conditions") and profile["health_conditions"]:
            conditions = ", ".join(profile["health_conditions"])
            lines.append(f"- Health Conditions: {conditions}")
        
        if profile.get("dietary_preferences") and profile["dietary_preferences"]:
            prefs = ", ".join(profile["dietary_preferences"])
            lines.append(f"- Dietary Preferences: {prefs}")
        
        if profile.get("health_goal") and profile["health_goal"] != "Not selected":
            lines.append(f"- Health Goal: {profile['health_goal']}")
        
        return "\n".join(lines) if lines else "No profile information provided"
