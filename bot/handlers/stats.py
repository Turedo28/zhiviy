from aiogram import Router, F
from aiogram.types import Message
import httpx

from bot.i18n import get_message
from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.config import bot_config

router = Router()


@router.message(F.text.contains("📊"))
async def show_statistics(message: Message):
    """Show daily statistics."""
    language = "uk"  # Get from user data in production

    # In production: fetch from backend API
    # For now, show placeholder stats

    stats_text = f"""
{get_message('daily_stats', language)}

{get_message('calories', language)}: 1,850 / 2,200 kcal
{get_message('protein', language)}: 85g / 150g
{get_message('carbs', language)}: 220g / 250g
{get_message('fats', language)}: 60g / 70g

📱 {get_message('visit_website', language)}
https://healthtrack.local/dashboard
    """

    keyboard = get_main_menu_keyboard(language)
    await message.answer(stats_text, reply_markup=keyboard)
