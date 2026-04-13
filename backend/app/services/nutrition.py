from datetime import date
from typing import Optional


def calculate_tdee(
    weight_kg: float,
    height_cm: float,
    age_years: int,
    gender: str,
    activity_level: str,
) -> float:
    """
    Calculate Total Daily Energy Expenditure using Mifflin-St Jeor equation.

    Activity levels:
    - sedentary: 1.2
    - light: 1.375
    - moderate: 1.55
    - active: 1.725
    - very_active: 1.9
    """
    # Mifflin-St Jeor BMR calculation
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
    else:  # female
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161

    # Activity multiplier
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }

    multiplier = activity_multipliers.get(activity_level, 1.55)
    tdee = bmr * multiplier

    return round(tdee, 0)


def calculate_macro_targets(
    tdee: float,
    goal: str,
    weight_kg: float,
) -> dict:
    """
    Calculate macro targets based on TDEE and goal.

    Goals:
    - lose: 300-500 calorie deficit, higher protein
    - maintain: maintenance, balanced macros
    - gain: 300-500 calorie surplus, high protein + carbs
    """
    targets = {}

    if goal == "lose":
        targets["calories"] = tdee - 400  # 400 calorie deficit
        targets["protein_g"] = weight_kg * 2.2  # 2.2g per kg (high protein for preservation)
    elif goal == "gain":
        targets["calories"] = tdee + 400  # 400 calorie surplus
        targets["protein_g"] = weight_kg * 1.8  # 1.8g per kg
    else:  # maintain
        targets["calories"] = tdee
        targets["protein_g"] = weight_kg * 1.6  # 1.6g per kg

    # Macro distribution
    targets["protein_g"] = round(targets["protein_g"], 1)
    targets["protein_cal"] = targets["protein_g"] * 4

    # 30% carbs, rest is fat
    targets["carbs_cal"] = targets["calories"] * 0.40
    targets["carbs_g"] = round(targets["carbs_cal"] / 4, 1)

    targets["fats_cal"] = targets["calories"] * 0.30
    targets["fats_g"] = round(targets["fats_cal"] / 9, 1)

    targets["calories"] = round(targets["calories"], 0)

    return targets


def calculate_age_from_dob(date_of_birth: date) -> int:
    """Calculate age from date of birth."""
    from datetime import date as date_class

    today = date_class.today()
    age = today.year - date_of_birth.year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age
