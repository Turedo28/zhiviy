import logging

import httpx
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.i18n import get_message
from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.config import bot_config

router = Router()
logger = logging.getLogger(__name__)

FRONTEND_URL = "https://zhiviy.com"


def _get_settings_keyboard() -> InlineKeyboardMarkup:
    """Settings inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Профіль", callback_data="settings_profile")],
            [InlineKeyboardButton(text="⌚ WHOOP підключення", callback_data="settings_whoop")],
            [InlineKeyboardButton(text="🌐 Відкрити сайт", url=f"{FRONTEND_URL}/dashboard")],
        ]
    )


@router.message(F.text.contains("⚙️"))
async def show_settings(message: Message):
    """Show settings menu."""
    keyboard = _get_settings_keyboard()
    await message.answer(
        "⚙️ <b>Налаштування</b>\n\n"
        "Оберіть розділ або відкрийте сайт для повного управління профілем:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "settings_profile")
async def show_profile(callback: CallbackQuery):
    """Show user profile info from backend."""
    telegram_id = callback.from_user.id

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{bot_config.API_BASE_URL}/dashboard/bot/{telegram_id}"
            response = await client.get(url, params={"telegram_id": telegram_id})

            if response.status_code != 200:
                await callback.message.edit_text(
                    "❌ Не вдалося завантажити профіль. Спробуйте пізніше."
                )
                await callback.answer()
                return

            data = response.json()
            if "error" in data:
                await callback.message.edit_text(
                    "⚠️ Профіль не знайдено. Натисніть /start для реєстрації."
                )
                await callback.answer()
                return

            name = data.get("user_name", "Користувач")
            whoop = "✅ Підключено" if data.get("whoop_connected") else "❌ Не підключено"
            plan = data.get("nutrition_plan")

            lines = [
                f"👤 <b>Профіль: {name}</b>\n",
                f"⌚ WHOOP: {whoop}",
            ]

            if plan:
                lines.append(f"🎯 Мета: {plan.get('goal_label', '—')}")
                lines.append(f"🔥 BMR: {plan.get('bmr', '—')} kcal")
                lines.append(f"⚡ TDEE: {plan.get('tdee', '—')} kcal")
                lines.append(f"🍽 Ціль калорій: {plan.get('target_calories', '—')} kcal")

            lines.append(f"\n📱 Повне управління на сайті:")
            lines.append(f"{FRONTEND_URL}/settings")

            await callback.message.edit_text(
                "\n".join(lines),
                parse_mode="HTML",
                reply_markup=_get_settings_keyboard(),
            )

    except Exception as e:
        logger.error(f"Settings profile error: {e}")
        await callback.message.edit_text("❌ Помилка завантаження профілю.")

    await callback.answer()


@router.callback_query(F.data == "settings_whoop")
async def show_whoop_status(callback: CallbackQuery):
    """Show WHOOP connection status."""
    telegram_id = callback.from_user.id

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{bot_config.API_BASE_URL}/dashboard/bot/{telegram_id}"
            response = await client.get(url, params={"telegram_id": telegram_id})

            if response.status_code == 200:
                data = response.json()
                connected = data.get("whoop_connected", False)

                if connected:
                    strain = data.get("strain")
                    recovery = data.get("recovery", {})
                    rec_score = recovery.get("score") if recovery else None

                    lines = [
                        "⌚ <b>WHOOP — Підключено</b> ✅\n",
                        f"💪 Навантаження: {round(strain, 1) if strain else '—'}",
                        f"🔋 Відновлення: {round(rec_score)}%" if rec_score else "🔋 Відновлення: —",
                        f"\n🔄 Синхронізація кожну годину",
                        f"\n📱 Керування: {FRONTEND_URL}/settings",
                    ]
                else:
                    lines = [
                        "⌚ <b>WHOOP — Не підключено</b>\n",
                        "Підключіть WHOOP на сайті для відстеження:",
                        "• Сну та якості сну",
                        "• Відновлення та HRV",
                        "• Навантаження та тренувань",
                        f"\n🔗 {FRONTEND_URL}/settings",
                    ]

                await callback.message.edit_text(
                    "\n".join(lines),
                    parse_mode="HTML",
                    reply_markup=_get_settings_keyboard(),
                )
            else:
                await callback.message.edit_text("❌ Не вдалося перевірити статус WHOOP.")

    except Exception as e:
        logger.error(f"WHOOP status error: {e}")
        await callback.message.edit_text("❌ Помилка перевірки WHOOP.")

    await callback.answer()
