import json
import os
from openai import OpenAI

# Configure OpenRouter API using the provided key
api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AI Fitness Tracker"
    }
)

def generate_diet_plan(
    calories: float,
    macros: dict,
    diet_preference: str,
    plan_duration: str,
    goal: str,
) -> dict:
    """
    Uses OpenRouter to generate a personalized diet plan using free models.
    """
    diet_label = diet_preference.replace("_", "-")
    num_days = 7 if plan_duration == "1_week" else 1

    prompt = f"""You are an expert nutritionist. Generate a detailed {diet_label} diet plan for {num_days} day(s).

**User Profile:**
- Daily Calorie Target: {calories} kcal
- Protein: {macros['protein_g']}g | Fat: {macros['fat_g']}g | Carbs: {macros['carbs_g']}g
- Diet Type: {diet_label}
- Fitness Goal: {goal.replace('_', ' ')}

**Rules:**
1. Each day must have 4 meals: breakfast, lunch, snack, dinner
2. Each meal must include: meal name, brief description, calories, protein_g, fat_g, carbs_g
3. Daily totals should be close to the target calories and macros
4. Use realistic, commonly available foods
5. {"Include only vegetarian foods (no meat, no fish, eggs allowed)" if diet_preference == "veg" else "Include only plant-based vegan foods (no meat, dairy, eggs, or honey)" if diet_preference == "vegan" else "Include a mix of vegetarian and non-vegetarian foods"}
6. Ensure variety across days if multi-day plan
7. Include Indian cuisine options where appropriate

**Respond ONLY with valid JSON in this exact format (no markdown, no code blocks, no extra text):**

{{
  "days": [
    {{
      "day": 1,
      "meals": {{
        "breakfast": {{
          "name": "Meal Name",
          "description": "Brief description",
          "calories": 400,
          "protein_g": 20,
          "fat_g": 12,
          "carbs_g": 50
        }},
        "lunch": {{
          "name": "Meal Name",
          "description": "Brief description",
          "calories": 500,
          "protein_g": 30,
          "fat_g": 15,
          "carbs_g": 60
        }},
        "snack": {{
          "name": "Meal Name",
          "description": "Brief description",
          "calories": 200,
          "protein_g": 10,
          "fat_g": 8,
          "carbs_g": 20
        }},
        "dinner": {{
          "name": "Meal Name",
          "description": "Brief description",
          "calories": 450,
          "protein_g": 25,
          "fat_g": 14,
          "carbs_g": 55
        }}
      }},
      "daily_total": {{
        "calories": 1550,
        "protein_g": 85,
        "fat_g": 49,
        "carbs_g": 185
      }}
    }}
  ]
}}"""

    try:
        response = client.chat.completions.create(
            model="google/gemma-3-12b-it:free",
            extra_body={
                "models": [
                    "google/gemma-3-12b-it:free",
                    "mistralai/mistral-small-3.1-24b-instruct:free"
                ]
            },
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        raw_text = response.choices[0].message.content.strip()

        # Clean up response - remove markdown code blocks if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]  # Remove first line
        if raw_text.endswith("```"):
            raw_text = raw_text.rsplit("```", 1)[0]  # Remove last ```
        raw_text = raw_text.strip()

        diet_plan = json.loads(raw_text)
        return {"status": "success", "plan": diet_plan}

    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Failed to parse AI response: {str(e)}"}
    except Exception as e:
        # Check if the error is a 429 rate limit or quota error from OpenRouter/OpenAI
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
            return {"status": "error", "message": "API Key Quota Hit. Please check your OpenRouter credits or try again later."}
        return {"status": "error", "message": f"OpenRouter API error: {str(e)}"}
