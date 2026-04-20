from aiogram import Router, F
from aiogram.types import Message
import httpx
import logging

from bot.i18n import get_message
from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.config import bot_config

router = Router()
logger = logging.getLogger(__name__)


def _progress_bar(current: float, target: float, width: int = 10) -> str:
    """Generate a text progress bar: [████░░░░░░] 65%"""
    if target <= 0:
        return "░" * width
    ratio = min(current / target, 1.0)
    filled = round(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    pct = round(ratio * 100)
    return f"{bar} {pct}%"


def _format_stats_message(data: dict) -> str:
    """Format the API response into a nice Telegram message."""
    n = data["nutrition"]
    burned = data["calories_burned"]
    water = data.get("water_ml", 0)
    water_target = data.get("water_target_ml", 3000)
    workouts = data.get("workouts", {})
    name = data.get("user_name", "")

    # Header
    lines = [f"📊 Статистика за сьогодні"]
    if name:
        lines[0] = f"📊 {name}, ваша статистика за сьогодні:"

    lines.append("")

    # Nutrition section
    lines.append("🍽 Харчування:")
    lines.append(
        f"  Калорії: {round(n['calories_consumed'])} / {round(n['calories_target'])} kcal"
    )
    lines.append(f"  {_progress_bar(n['calories_consumed'], n['calories_target'])}")
    lines.append(f"  Білки: {round(n['protein_g'])}г / {round(n['protein_target'])}г")
    lines.append(f"  Вуглеводи: {round(n['carbs_g'])}г / {round(n['carbs_target'])}г")
    lines.append(f"  Жири: {round(n['fats_g'])}г / {round(n['fats_target'])}г")

    meals_count = n.get("meals_count", 0)
    if meals_count > 0:
        lines.append(f"  Прийомів їжі: {meals_count}")
    else:
        lines.append("  Прийомів їжі: 0 — додайте перший! ➕")

    lines.append("")

    # Calories burned section
    lines.append("🔥 Витрачено калорій:")
    lines.append(f"  Загалом: {burned['total']} kcal")
    lines.append(f"  ├ Базовий обмін (BMR): {burned['bmr']} kcal")
    lines.append(f"  ├ Активність (NEAT): {burned['neat']} kcal")
    lines.append(f"  ├ Переварювання їжі (TEF): {burned['tef']} kcal")
    lines.append(f"  └ Тренування: {burned['exercise']} kcal")

    source_label = {
        "whoop": "WHOOP",
        "apple_health": "Apple Health",
        "calculated": "Розрахунок",
        "incomplete_profile": "Заповніть профіль",
    }
    lines.append(f"  Джерело: {source_label.get(burned['source'], burned['source'])}")

    lines.append("")

    # Water section
    lines.append("💧 Вода:")
    lines.append(f"  {round(water)} / {round(water_target)} мл")
    lines.append(f"  {_progress_bar(water, water_target)}")

    lines.append("")

    # Workouts section
    w_count = workouts.get("count", 0)
    if w_count > 0:
        lines.append(f"🏋️ Тренування сьогодні: {w_count}")
        for w in workouts.get("workouts", []):
            sport = w.get("sport", "Тренування")
            cal = w.get("calories", 0)
            dur = w.get("duration_min", 0)
            lines.append(f"  • {sport}: {cal} kcal, {dur} хв")
    else:
        lines.append("🏋️ Тренувань сьогодні: 0")

    lines.append("")

    # Goal
    goal_label = n.get("goal_label", "")
    if goal_label:
        lines.append(f"🎯 Мета: {goal_label}")
        lines.append("")

    # Calorie balance
    balance = round(n["calories_consumed"]) - burned["total"]
    if balance > 0:
        lines.append(f"⚖️ Баланс: +{balance} kcal (надлишок)")
    else:
        lines.append(f"⚖️ Баланс: {balance} kcal (дефіцит)")

    lines.append("")
    lines.append("📱 Детальніше на сайті:")
    lines.append("https://zhiviy.com/dashboard")

    return "\n".join(lines)


@router.message(F.text.contains("📊"))
async def show_statistics(message: Message):
    """Show daily statistics fetched from backend API."""
    language = "uk"
    keyboard = get_main_menu_keyboard(language)

    telegram_id = message.from_user.id

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{bot_config.API_BASE_URL}/dashboard/today/demo"
            response = await client.get(url, params={"telegram_id": telegram_id})

            if response.status_code != 200:
                logger.error(f"Stats API returned {response.status_code}: {response.text}")
                await message.answer(
                    f"❌ {get_message('error', language)}",
                    reply_markup=keyboard,
                )
                return

            data = response.json()

            if "error" in data:
                if data.get("code") == "USER_NOT_FOUND":
                    await message.answer(
                        "⚠️ Ваш профіль не знайдено. Натисніть /start щоб зареєструватись.",
                        reply_markup=keyboard,
                    )
                else:
                    await message.answer(
                        f"❌ {get_message('error', language)}",
                        reply_markup=keyboard,
                    )
                return

            stats_text = _format_stats_message(data)
            await message.answer(stats_text, reply_markup=keyboard)

    except httpx.TimeoutException:
        logger.error("Stats API timeout")
        await message.answer(
            "⏳ Сервер не відповідає. Спробуйте пізніше.",
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.error(f"Stats handler error: {e}", exc_info=True)
        await message.answer(
            f"❌ {get_message('error', language)}",
            reply_markup=keyboard,
        )
