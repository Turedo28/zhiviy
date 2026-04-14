"""
Nutrition calculation service.
Calculates TDEE, calorie targets, and macro targets based on user profile,
fitness goal, and WHOOP activity data (Day Strain, burned calories).
"""
from datetime import date
from typing import Optional, Dict, Any, List


def calculate_age_from_dob(date_of_birth: date) -> int:
    """Calculate age from date of birth."""
    today = date.today()
    age = today.year - date_of_birth.year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor BMR Equation."""
    if gender.lower() == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Calculate Total Daily Energy Expenditure."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier)


def calculate_target_calories(tdee: float, goal: str) -> int:
    """Apply caloric adjustment based on goal."""
    adjustments = {"lose": -400, "maintain": 0, "gain": 400}
    return round(tdee + adjustments.get(goal, 0))


def calculate_macros(
    target_calories: int,
    weight_kg: float,
    goal: str,
    day_strain: Optional[float] = None,
) -> Dict[str, float]:
    """
    Calculate macro targets (protein, carbs, fats) in grams.
    Adjusts protein upward based on WHOOP Day Strain.
    """
    # Base protein per kg based on goal
    protein_map = {"gain": 2.0, "lose": 2.2, "maintain": 1.6}
    protein_per_kg = protein_map.get(goal, 1.6)

    # Strain-based protein boost
    if day_strain is not None:
        if day_strain >= 15:
            protein_per_kg += 0.3
        elif day_strain >= 10:
            protein_per_kg += 0.15

    protein_g = round(weight_kg * protein_per_kg)

    # Fat: 25% on cut, 30% otherwise
    fat_pct = 0.25 if goal == "lose" else 0.30
    fats_g = round(target_calories * fat_pct / 9)

    # Carbs: remainder
    carbs_g = max(round((target_calories - protein_g * 4 - fats_g * 9) / 4), 50)

    return {
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fats_g": fats_g,
    }


GOAL_LABELS = {
    "lose": "Похудение",
    "maintain": "Поддержание",
    "gain": "Набор массы",
}

GOAL_LABELS_UK = {
    "lose": "Схуднення",
    "maintain": "Підтримка",
    "gain": "Набір маси",
}


def _build_recommendations(
    goal: str,
    day_strain: Optional[float],
    target_calories: int,
    macros: Dict[str, float],
) -> List[Dict[str, str]]:
    """Generate smart nutrition recommendations based on goal + strain."""
    recs: List[Dict[str, str]] = []

    if day_strain is not None:
        if day_strain >= 14 and goal != "gain":
            recs.append({
                "type": "protein",
                "icon": "💪",
                "text": "Высокая нагрузка сегодня — добавьте белка для сохранения мышц",
            })
        if day_strain >= 16 and goal == "lose":
            recs.append({
                "type": "carbs",
                "icon": "⚡",
                "text": "Очень высокая нагрузка на дефиците — добавьте углеводов для восстановления",
            })
        if day_strain < 5 and goal == "gain":
            recs.append({
                "type": "training",
                "icon": "🏋️",
                "text": "Низкая нагрузка при наборе массы — увеличьте интенсивность тренировки",
            })
        if day_strain >= 10:
            recs.append({
                "type": "water",
                "icon": "💧",
                "text": "При нагрузке выше 10 пейте не менее 3 л воды",
            })

    if goal == "lose" and target_calories < 1500:
        recs.append({
            "type": "warning",
            "icon": "⚠️",
            "text": "Калорийность ниже 1500 — не рекомендуется длительный дефицит",
        })

    return recs


def get_nutrition_plan(
    weight_kg: float,
    height_cm: float,
    date_of_birth: date,
    gender: str,
    activity_level: str,
    goal: str,
    day_strain: Optional[float] = None,
    calories_burned: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Build a complete nutrition plan based on user profile and WHOOP data.
    Returns BMR, TDEE, target calories, macros, and smart recommendations.
    """
    age = calculate_age_from_dob(date_of_birth)
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    target_cal = calculate_target_calories(tdee, goal)
    macros = calculate_macros(target_cal, weight_kg, goal, day_strain)
    recommendations = _build_recommendations(goal, day_strain, target_cal, macros)

    return {
        "bmr": round(bmr),
        "tdee": tdee,
        "target_calories": target_cal,
        "macros": macros,
        "goal": goal,
        "goal_label": GOAL_LABELS.get(goal, goal),
        "calories_burned": round(calories_burned) if calories_burned else 0,
        "day_strain": round(day_strain, 1) if day_strain is not None else None,
        "recommendations": recommendations,
    }
