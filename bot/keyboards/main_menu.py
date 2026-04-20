from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot.i18n import get_message


def get_main_menu_keyboard(language: str = "uk") -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_message("add_meal", language))],
            [KeyboardButton(text=get_message("statistics", language)), KeyboardButton(text="💧 Вода")],
            [KeyboardButton(text=get_message("settings", language))],
        ],
        resize_keyboard=True,
    )


def get_language_choice_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Українська", callback_data="lang_uk"),
                InlineKeyboardButton(text="English", callback_data="lang_en"),
            ]
        ]
    )


def get_meal_confirmation_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Get meal confirmation keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_message("confirm", language),
                    callback_data="meal_confirm",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_message("edit", language),
                    callback_data="meal_edit",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_message("cancel", language),
                    callback_data="meal_cancel",
                ),
            ],
        ]
    )


def get_cancel_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_message("cancel", language),
                    callback_data="cancel",
                )
            ]
        ]
    )
