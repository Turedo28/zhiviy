import base64
import json
import logging

from anthropic import Anthropic
from bot.config import bot_config

logger = logging.getLogger(__name__)

client = Anthropic(api_key=bot_config.ANTHROPIC_API_KEY)


async def analyze_food_photo(image_data: bytes) -> dict:
    """
    Analyze food photo using Claude Vision API.
    Returns dict with name, calories, protein, carbs, fats, confidence.
    """
    base64_image = base64.standard_b64encode(image_data).decode("utf-8")

    prompt = """Проаналізуй це фото їжі та визнач поживну цінність.

    Поверни ТІЛЬКИ JSON об'єкт (без markdown, без пояснень) з полями:
    - name: назва страви українською (string)
    - description: короткий опис порції українською (string, max 80 символів)
    - calories: калорійність (number)
    - protein_g: білки в грамах (number)
    - carbs_g: вуглеводи в грамах (number)
    - fats_g: жири в грамах (number)
    - fiber_g: клітковина в грамах (number)
    - weight_g: приблизна вага порції в грамах (number)
    - confidence: рівень впевненості (string: "high", "medium", "low")

    Будь реалістичним з порціями. Якщо не впевнений — використовуй консервативні оцінки.
    Оцінюй на основі видимого розміру порції.

    Приклад:
    {"name": "Куряча грудка з рисом", "description": "Грильована курка з білим рисом та овочами", "calories": 450, "protein_g": 40, "carbs_g": 45, "fats_g": 8, "fiber_g": 3, "weight_g": 350, "confidence": "high"}
    """

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            temperature=0,
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

        # Clean up response if wrapped in markdown code block
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0].strip()

        analysis = json.loads(response_text)

        return {
            "success": True,
            "name": analysis.get("name", "Невідома страва"),
            "description": analysis.get("description", ""),
            "calories": float(analysis.get("calories", 0)),
            "protein_g": float(analysis.get("protein_g", 0)),
            "carbs_g": float(analysis.get("carbs_g", 0)),
            "fats_g": float(analysis.get("fats_g", 0)),
            "fiber_g": float(analysis.get("fiber_g", 0)),
            "weight_g": float(analysis.get("weight_g", 0)),
            "confidence": analysis.get("confidence", "medium"),
        }

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response: {e}")
        return {"success": False, "error": "Не вдалося розпізнати відповідь AI"}
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return {"success": False, "error": f"Помилка AI: {str(e)}"}


async def analyze_food_text(text: str) -> dict:
    """
    Analyze food description text using Claude API.
    Returns dict with name, calories, protein, carbs, fats, confidence.
    """
    prompt = f"""Користувач описав що він з'їв: "{text}"

    Проаналізуй цей опис їжі та визнач поживну цінність.

    ВАЖЛИВО — правила визначення назви:
    1. Якщо користувач перелічує окремі інгредієнти з вагою (наприклад "72г огурців, 28г помідорів, 106г креветок") — це НЕ салат. Це скоріш за все боул (bowl) або складена порція. Назви це "Боул" або "Порція" з переліком головних інгредієнтів.
    2. Салат — це коли явно сказано "салат" або є заправка (олія, соус, майонез).
    3. Кожен інгредієнт рахуй ОКРЕМО за вказаною вагою — НЕ угадуй порцію, а рахуй точно по грамах.
    4. Загальна вага = сума всіх вказаних грамів.

    ВАЖЛИВО — транслітерація та сленг:
    Користувачі часто пишуть англійські назви кирилицею. Розпізнавай:
    "айс латте"/"айс лате" = ice latte, "чізкейк" = cheesecake, "смузі" = smoothie,
    "капучіно" = cappuccino, "матча латте" = matcha latte, "раф" = raf coffee,
    "флет вайт" = flat white, "бургер" = burger, "наггетси" = nuggets, "стейк" = steak,
    "сендвіч" = sandwich, "брауні" = brownie, "панкейки" = pancake, "гранола" = granola,
    "протеїн шейк" = protein shake, "боул"/"поке боул" = bowl/poke bowl,
    "амер"/"америк" = американо, "лонг блек" = long black.
    Текст може бути українською, російською або суржиком — розпізнавай все.

    Поверни ТІЛЬКИ JSON об'єкт (без markdown, без пояснень) з полями:
    - name: назва страви українською (string). Якщо це список інгредієнтів — назви "Боул" або "Порція", НЕ "Салат".
    - description: короткий опис порції українською (string, max 80 символів). Перелічи головні інгредієнти.
    - calories: калорійність (number) — рахуй КОЖЕН інгредієнт окремо по КБЖУ таблицях
    - protein_g: білки в грамах (number)
    - carbs_g: вуглеводи в грамах (number)
    - fats_g: жири в грамах (number)
    - fiber_g: клітковина в грамах (number)
    - weight_g: загальна вага порції в грамах = сума всіх вказаних грамів (number)
    - confidence: рівень впевненості (string: "high" якщо вказано грами, "medium", "low")

    Якщо вказано точну вагу — confidence = "high".
    Якщо це відомий продукт або напій — використай стандартні КБЖУ.

    Приклад:
    {{"name": "Боул з креветками", "description": "Огірки, помідори черрі, редис, відварені креветки, яєчний білок", "calories": 142, "protein_g": 26.5, "carbs_g": 5.2, "fats_g": 1.8, "fiber_g": 1.5, "weight_g": 288, "confidence": "high"}}
    """

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        response_text = message.content[0].text.strip()

        # Clean up response if wrapped in markdown code block
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0].strip()

        analysis = json.loads(response_text)

        return {
            "success": True,
            "name": analysis.get("name", "Невідома страва"),
            "description": analysis.get("description", ""),
            "calories": float(analysis.get("calories", 0)),
            "protein_g": float(analysis.get("protein_g", 0)),
            "carbs_g": float(analysis.get("carbs_g", 0)),
            "fats_g": float(analysis.get("fats_g", 0)),
            "fiber_g": float(analysis.get("fiber_g", 0)),
            "weight_g": float(analysis.get("weight_g", 0)),
            "confidence": analysis.get("confidence", "medium"),
        }

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude text response: {e}")
        return {"success": False, "error": "Не вдалося розпізнати відповідь AI"}
    except Exception as e:
        logger.error(f"Claude API error (text): {e}")
        return {"success": False, "error": f"Помилка AI: {str(e)}"}
