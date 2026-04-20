import io
import logging

import httpx
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.i18n import get_message
from bot.config import bot_config
from bot.keyboards.main_menu import get_meal_confirmation_keyboard, get_main_menu_keyboard
from bot.services.claude_vision import analyze_food_photo
from bot.services.sync_queue import enqueue_meal

logger = logging.getLogger(__name__)

router = Router()


class MealAddState(StatesGroup):
    """FSM states for meal adding flow."""
    waiting_for_input = State()
    waiting_for_photo = State()
    waiting_for_confirmation = State()


def format_confidence(confidence: str) -> str:
    """Format confidence level with emoji."""
    mapping = {
        "high": "🟢 Висока",
        "medium": "🟡 Середня",
        "low": "🔴 Низька",
    }
    return mapping.get(confidence, "🟡 Середня")


def format_analysis(data: dict) -> str:
    """Format food analysis into a nice message."""
    conf = format_confidence(data.get("confidence", "medium"))

    return (
        f"📸 <b>{data['name']}</b>\n"
        f"{data.get('description', '')}\n\n"
        f"⚡ Калорії: <b>{data['calories']:.0f}</b> kcal\n"
        f"🥩 Білки: <b>{data['protein_g']:.1f}</b>г\n"
        f"🍚 Вуглеводи: <b>{data['carbs_g']:.1f}</b>г\n"
        f"🧈 Жири: <b>{data['fats_g']:.1f}</b>г\n"
        f"🌾 Клітковина: <b>{data.get('fiber_g', 0):.1f}</b>г\n"
        f"⚖️ Порція: ~<b>{data.get('weight_g', 0):.0f}</b>г\n\n"
        f"📊 Впевненість: {conf}"
    )


@router.message(F.text == get_message("add_meal", "uk"))
async def add_meal_start_uk(message: Message, state: FSMContext):
    """Start meal adding flow (Ukrainian)."""
    await message.answer("📷 Надішліть фото страви або опишіть що ви з'їли текстом:")
    await state.set_state(MealAddState.waiting_for_input)


@router.message(F.text == get_message("add_meal", "en"))
async def add_meal_start_en(message: Message, state: FSMContext):
    """Start meal adding flow (English)."""
    await message.answer("📷 Send a photo of your meal or describe what you ate:")
    await state.set_state(MealAddState.waiting_for_input)


@router.message(MealAddState.waiting_for_input, F.photo)
async def process_meal_photo(message: Message, state: FSMContext, bot: Bot):
    """Process meal photo with Claude Vision."""
    language = "uk"

    # Show typing indicator
    processing_msg = await message.answer("🔍 Аналізую фото страви...")

    try:
        # Download photo from Telegram
        photo = message.photo[-1]  # Best quality
        file = await bot.get_file(photo.file_id)
        photo_bytes = io.BytesIO()
        await bot.download_file(file.file_path, photo_bytes)
        image_data = photo_bytes.getvalue()

        # Analyze with Claude Vision
        result = await analyze_food_photo(image_data)

        if not result.get("success"):
            error_msg = result.get("error", "Невідома помилка")
            await processing_msg.edit_text(f"❌ {error_msg}\n\nСпробуйте інше фото.")
            return

        # Format and show analysis
        analysis_text = format_analysis(result)

        # Save data in FSM for confirmation
        await state.update_data(
            photo_file_id=photo.file_id,
            analysis=result,
        )

        keyboard = get_meal_confirmation_keyboard(language)
        await processing_msg.edit_text(analysis_text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(MealAddState.waiting_for_confirmation)

    except Exception as e:
        logger.error(f"Error processing meal photo: {e}")
        await processing_msg.edit_text(
            "❌ Виникла помилка при аналізі фото.\nСпробуйте ще раз."
        )


@router.message(MealAddState.waiting_for_input, F.text)
async def process_meal_text(message: Message, state: FSMContext):
    """Process meal text description with Claude analysis."""
    from bot.services.claude_vision import analyze_food_text
    language = "uk"
    processing_msg = await message.answer("🔍 Аналізую опис страви...")

    try:
        result = await analyze_food_text(message.text)
        if not result.get("success"):
            error_msg = result.get("error", "Невідома помилка")
            await processing_msg.edit_text(f"❌ {error_msg}")
            return

        analysis_text = format_analysis(result)
        await state.update_data(analysis=result)

        keyboard = get_meal_confirmation_keyboard(language)
        await processing_msg.edit_text(analysis_text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(MealAddState.waiting_for_confirmation)
    except Exception as e:
        logger.error(f"Error processing meal text: {e}")
        await processing_msg.edit_text("❌ Виникла помилка. Спробуйте ще раз.")


@router.callback_query(MealAddState.waiting_for_confirmation, F.data == "meal_confirm")
async def confirm_meal(callback: CallbackQuery, state: FSMContext):
    """Confirm meal addition and save to backend."""
    data = await state.get_data()
    analysis = data.get("analysis", {})
    telegram_id = callback.from_user.id

    # Save meal to backend API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{bot_config.API_BASE_URL}/meals/bot",
                json={
                    "telegram_id": telegram_id,
                    "name": analysis.get("name", "Невідома страва"),
                    "description": analysis.get("description", ""),
                    "calories": analysis.get("calories", 0),
                    "protein_g": analysis.get("protein_g", 0),
                    "carbs_g": analysis.get("carbs_g", 0),
                    "fats_g": analysis.get("fats_g", 0),
                    "fiber_g": analysis.get("fiber_g", 0),
                    "weight_g": analysis.get("weight_g", 0),
                    "confidence": analysis.get("confidence", "medium"),
                },
                timeout=10,
            )
            saved = response.status_code in (200, 201)
    except Exception as e:
        logger.error(f"Failed to save meal to backend: {e}")
        saved = False

    meal_payload = {
        "telegram_id": telegram_id,
        "name": analysis.get("name", "Невідома страва"),
        "description": analysis.get("description", ""),
        "calories": analysis.get("calories", 0),
        "protein_g": analysis.get("protein_g", 0),
        "carbs_g": analysis.get("carbs_g", 0),
        "fats_g": analysis.get("fats_g", 0),
        "fiber_g": analysis.get("fiber_g", 0),
        "weight_g": analysis.get("weight_g", 0),
        "confidence": analysis.get("confidence", "medium"),
    }

    if saved:
        success_text = (
            f"✅ <b>Прийом їжі збережено!</b>\n\n"
            f"🍽 {analysis.get('name', 'Страва')}: "
            f"{analysis.get('calories', 0):.0f} kcal"
        )
    else:
        # Queue for retry
        enqueue_meal(meal_payload)
        success_text = (
            f"⚠️ <b>Збережено локально, синхронізую пізніше.</b>\n\n"
            f"🍽 {analysis.get('name', 'Страва')}: "
            f"{analysis.get('calories', 0):.0f} kcal"
        )

    await callback.message.edit_text(success_text, parse_mode="HTML")
    await state.clear()
    await callback.answer("Збережено!" if saved else "Помилка збереження")


@router.callback_query(MealAddState.waiting_for_confirmation, F.data == "meal_edit")
async def edit_meal(callback: CallbackQuery, state: FSMContext):
    """Edit meal - ask for new photo or text."""
    await callback.message.edit_text("📷 Надішліть нове фото або введіть назву страви:")
    await state.set_state(MealAddState.waiting_for_input)
    await callback.answer()


@router.callback_query(MealAddState.waiting_for_confirmation, F.data == "meal_cancel")
async def cancel_meal(callback: CallbackQuery, state: FSMContext):
    """Cancel meal addition."""
    await callback.message.edit_text("❌ Прийом їжі скасовано.")
    await state.clear()
    await callback.answer()
