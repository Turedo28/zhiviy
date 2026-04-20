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
    if target <= 0:
        return "░" * width
    ratio = min(current / target, 1.0)
    filled = round(ratio * width)
    return f"{'█' * filled}{'░' * (width - filled)} {round(ratio * 100)}%"


def _format_stats_message(data: dict) -> str:
    n = data["nutrition"]
    name = data.get("user_name", "")
    plan = data.get("nutrition_plan")
    water = data.get("water") or {}
    workouts = data.get("workouts") or []
    recovery = data.get("recovery") or {}
    strain = data.get("strain")

    lines = [f"📊 {name}, ваша статистика за сьогодні:" if name else "📊 Статистика за сьогодні", ""]

    # Nutrition
    lines.append("🍽 Харчування:")
    lines.append(f"  Калорії: {round(n['calories_consumed'])} / {round(n['calories_target'])} kcal")
    lines.append(f"  {_progress_bar(n['calories_consumed'], n['calories_target'])}")
    lines.append(f"  Білки: {round(n['protein_g'])}г / {round(n['protein_target'])}г")
    lines.append(f"  Вуглеводи: {round(n['carbs_g'])}г / {round(n['carbs_target'])}г")
    lines.append(f"  Жири: {round(n['fats_g'])}г / {round(n['fats_target'])}г")
    meals_count = len(n.get("meals") or [])
    lines.append(f"  Прийомів їжі: {meals_count}" if meals_count else "  Прийомів їжі: 0 — додайте перший! ➕")
    lines.append("")

    # Calories burned / plan
    if plan:
        burned = round(plan.get("calories_burned") or 0)
        tdee = plan.get("tdee") or 0
        lines.append("🔥 Витрачено калорій:")
        lines.append(f"  Загалом (TDEE): {tdee} kcal")
        lines.append(f"  BMR: {plan.get('bmr', '—')} kcal")
        if burned:
            lines.append(f"  Тренування: {burned} kcal")
        lines.append("")

    # Water
    if water:
        consumed = water.get("consumed_ml", 0)
        target = water.get("target_ml", 2500)
        lines.append("💧 Вода:")
        lines.append(f"  {consumed} / {target} мл")
        lines.append(f"  {_progress_bar(consumed, target)}")
        lines.append("")

    # Workouts
    if workouts:
        lines.append(f"🏋️ Тренування сьогодні: {len(workouts)}")
        for w in workouts:
            lines.append(f"  • {w.get('sport_name', 'Тренування')}: {w.get('calories', 0)} kcal, {w.get('duration_min', 0)} хв")
        lines.append("")
    else:
        lines.append("🏋️ Тренувань сьогодні: 0")
        lines.append("")

    # Recovery / Strain
    if strain is not None:
        lines.append(f"💪 Навантаження (strain): {round(strain, 1)}")
    rec_score = recovery.get("score")
    if rec_score is not None:
        lines.append(f"🔋 Відновлення: {round(rec_score)}%")
    if strain is not None or rec_score is not None:
        lines.append("")

    # Goal
    if plan and plan.get("goal_label"):
        lines.append(f"🎯 Мета: {plan['goal_label']}")
        balance = round(n["calories_consumed"]) - round(plan.get("tdee") or n["calories_target"])
        lines.append(f"⚖️ Баланс: {'+' if balance > 0 else ''}{balance} kcal")
        lines.append("")

    lines.append("📱 Детальніше: https://zhiviy.com/dashboard")
    return "\n".join(lines)


@router.message(F.text.contains("📊"))
async def show_statistics(message: Message):
    language = "uk"
    keyboard = get_main_menu_keyboard(language)
    telegram_id = message.from_user.id

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{bot_config.API_BASE_URL}/dashboard/bot/{telegram_id}",
            )

            if response.status_code == 404:
                await message.answer(
                    "⚠️ Ваш профіль не знайдено. Натисніть /start щоб зареєструватись.",
                    reply_markup=keyboard,
                )
                return

            if response.status_code != 200:
                logger.error(f"Stats API returned {response.status_code}: {response.text}")
                await message.answer(f"❌ {get_message('error', language)}", reply_markup=keyboard)
                return

            stats_text = _format_stats_message(response.json())
            await message.answer(stats_text, reply_markup=keyboard)

    except httpx.TimeoutException:
        await message.answer("⏳ Сервер не відповідає. Спробуйте пізніше.", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Stats handler error: {e}", exc_info=True)
        await message.answer(f"❌ {get_message('error', language)}", reply_markup=keyboard)
