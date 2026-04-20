import logging

import httpx
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import bot_config
from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.services.reminders import register_user

router = Router()
logger = logging.getLogger(__name__)

AMOUNTS = [250, 500, 750, 1000]


def _water_keyboard():
    builder = InlineKeyboardBuilder()
    for ml in AMOUNTS:
        builder.button(text=f"+{ml}мл", callback_data=f"water_{ml}")
    builder.adjust(4)
    return builder.as_markup()


@router.message(F.text.contains("💧"))
async def water_menu(message: Message):
    telegram_id = message.from_user.id
    register_user(telegram_id)

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(f"{bot_config.API_BASE_URL}/water/today/bot/{telegram_id}")
            if res.status_code == 200:
                d = res.json()
                consumed = d.get("consumed_ml", 0)
                target = d.get("target_ml", 2500)
                pct = d.get("percentage", 0)
                status = f"💧 Сьогодні: {consumed}/{target}мл ({pct}%)"
            else:
                status = "💧 Вода"
    except Exception:
        status = "💧 Вода"

    await message.answer(
        f"{status}\n\nСкільки додати?",
        reply_markup=_water_keyboard(),
    )


@router.callback_query(F.data.startswith("water_"))
async def add_water(callback: CallbackQuery):
    ml = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.post(
                f"{bot_config.API_BASE_URL}/water/bot/{telegram_id}",
                json={"amount_ml": ml},
            )
            if res.status_code in (200, 201):
                d = res.json()
                total = d.get("total_today_ml", 0)
                target = d.get("target_ml", 2500)
                pct = d.get("percentage", 0)
                await callback.message.edit_text(
                    f"✅ Додано {ml}мл!\n\n💧 Сьогодні: {total}/{target}мл ({pct}%)",
                    reply_markup=_water_keyboard(),
                )
            else:
                await callback.answer("Помилка збереження", show_alert=True)
                return
    except Exception as e:
        logger.error(f"Water add error: {e}")
        await callback.answer("Сервер не відповідає", show_alert=True)
        return

    await callback.answer(f"💧 +{ml}мл")
