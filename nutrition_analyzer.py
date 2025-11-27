"""
EatWise AI - Ultra-Minimal Nutrition Analyzer
Pure LLM-powered analysis with only 3 core methods
"""

import json
import base64
from typing import Dict, Optional
from openai import AzureOpenAI


class NutritionAnalyzer:
    """Analyzes food using Azure OpenAI GPT-4 Vision and GPT-4 (HKUST endpoint)"""
    
    def __init__(self, api_key: str, endpoint: str = None, deployment: str = None):
        """Initialize with Azure OpenAI API key and endpoint
        
        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint (defaults to HKUST)
            deployment: Deployment name (defaults to gpt-4o)
        """
        if not api_key:
            raise ValueError("Azure OpenAI API key is required. Please set AZURE_OPENAI_API_KEY in your .env file")
        
        self.api_key = api_key
        self.endpoint = endpoint or "https://hkust.azure-api.net/"
        self.deployment = deployment or "gpt-4o"
        
        try:
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version="2024-05-01-preview",
                azure_endpoint=self.endpoint
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Azure OpenAI client: {str(e)}. Please verify your API key and endpoint are correct.")
    
    def detect_food_from_image(self, image_data: bytes, profile: Dict) -> str:
        """
        Detect food from image and provide nutrition analysis with personalized tips.
        
        Args:
            image_data: Image bytes
            profile: User profile (name, age_group, health_conditions, dietary_preferences, health_goal)
            
        Returns:
            Formatted markdown string with analysis
        """
        try:
            # Convert image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Build personalization context
            context = self._build_profile_context(profile)
            
            prompt = f"""Analyze this food image and provide:
1. Detected food items and quantities
2. Estimated nutrition (calories, protein, carbs, fat, fiber, sodium, sugar)
3. Health rating (1-10)
4. Personalized tips based on the user profile

User Profile:
{context}

Format your response as a clear, readable paragraph. Include nutrition estimates and personalized health advice."""
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"Image analysis error: {str(e)}")
    
    def analyze_text_meal(self, meal_description: str, profile: Dict) -> str:
        """
        Analyze meal from text description and provide personalized nutrition insights.
        
        Args:
            meal_description: Text description of the meal
            profile: User profile (name, age_group, health_conditions, dietary_preferences, health_goal)
            
        Returns:
            Formatted markdown string with analysis
        """
        try:
            # Build personalization context
            context = self._build_profile_context(profile)
            
            prompt = f"""Analyze this meal and provide:
1. Identified food items and estimated portions
2. Estimated nutrition (calories, protein, carbs, fat, fiber, sodium, sugar)
3. Health rating (1-10)
4. Personalized recommendations based on user profile
5. How it aligns with their health goal

User Profile:
{context}

Meal Description: {meal_description}

Format your response as a clear, readable paragraph with practical advice."""
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a nutrition expert. Provide accurate nutritional analysis and personalized health recommendations in paragraph format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        
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
