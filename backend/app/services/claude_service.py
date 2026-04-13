import base64
import json
from typing import Optional

from anthropic import Anthropic

from app.core.config import settings

client = Anthropic()


async def analyze_food_photo(image_data: bytes) -> dict:
    """
    Analyze food photo using Claude Vision API.

    Returns: {
        "name": "string",
        "description": "string",
        "calories": float,
        "protein_g": float,
        "carbs_g": float,
        "fats_g": float,
        "confidence": "high" | "medium" | "low"
    }
    """
    base64_image = base64.standard_b64encode(image_data).decode("utf-8")

    prompt = """Analyze this food image and provide nutritional information.

    Return ONLY a JSON object (no markdown, no explanation) with these fields:
    - name: the food name (string)
    - description: brief description of the meal (string, max 100 chars)
    - calories: estimated calories (number)
    - protein_g: estimated protein in grams (number)
    - carbs_g: estimated carbs in grams (number)
    - fats_g: estimated fats in grams (number)
    - confidence: your confidence level (string: "high", "medium", or "low")

    Be realistic with portions. If unsure about amounts, use conservative estimates.

    Example output:
    {"name": "Grilled Chicken Breast", "description": "With rice and vegetables", "calories": 450, "protein_g": 40, "carbs_g": 45, "fats_g": 8, "confidence": "high"}
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    )

    response_text = message.content[0].text.strip()

    # Parse JSON response
    analysis = json.loads(response_text)

    return {
        "name": analysis.get("name", "Unknown"),
        "description": analysis.get("description", ""),
        "calories": float(analysis.get("calories", 0)),
        "protein_g": float(analysis.get("protein_g", 0)),
        "carbs_g": float(analysis.get("carbs_g", 0)),
        "fats_g": float(analysis.get("fats_g", 0)),
        "confidence": analysis.get("confidence", "medium"),
    }


async def generate_health_recommendation(
    health_data: dict,
    language: str = "uk",
) -> str:
    """
    Generate personalized health recommendations using Claude.

    health_data should contain: sleep, stress, activity, nutrition data, etc.
    """
    language_name = "Ukrainian" if language == "uk" else "English"

    prompt = f"""Based on this health data, provide 3-4 personalized health recommendations.

    Health Data:
    {json.dumps(health_data, indent=2, ensure_ascii=False)}

    Respond in {language_name} language.
    Be concise and actionable. Focus on improvements the person can make.
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return message.content[0].text


async def parse_blood_work(
    image_data: bytes,
    language: str = "uk",
) -> dict:
    """
    Parse blood work results from an image using Claude Vision.

    Returns: {
        "biomarkers": [
            {"name": "string", "value": float, "unit": "string", "status": "normal|low|high"}
        ],
        "summary": "string",
        "recommendations": [list of recommendations]
    }
    """
    base64_image = base64.standard_b64encode(image_data).decode("utf-8")

    language_name = "Ukrainian" if language == "uk" else "English"

    prompt = f"""Extract biomarkers from this blood work image.

    Return ONLY a JSON object with:
    - biomarkers: array of {{name, value, unit, status}}
    - summary: brief interpretation in {language_name}
    - recommendations: array of improvement suggestions in {language_name}

    For status, use: "normal", "low", or "high" based on typical reference ranges.
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    )

    response_text = message.content[0].text.strip()
    result = json.loads(response_text)

    return result
