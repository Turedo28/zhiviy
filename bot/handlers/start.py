from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from bot.i18n import get_message
from bot.keyboards.main_menu import get_language_choice_keyboard, get_main_menu_keyboard
from bot.config import bot_config

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    welcome_text = f"{get_message('welcome', 'uk')}\n\n{first_name}!"

    keyboard = get_language_choice_keyboard()
    await message.answer(welcome_text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("lang_"))
async def process_language_choice(callback: CallbackQuery):
    """Handle language selection."""
    language = callback.data.split("_")[1]

    # Store language preference (would be saved to DB in production)
    main_menu_text = get_message("main_menu", language)
    keyboard = get_main_menu_keyboard(language)

    await callback.message.delete()
    await callback.message.answer(main_menu_text, reply_markup=keyboard)
    await callback.answer()
