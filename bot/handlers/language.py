from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.services.i18n import I18n
from bot.database.crud import update_user_language
from bot.keyboards.inline_keyboards import get_language_keyboard

router = Router()


@router.message(Command("language"))
async def language_handler(message: types.Message, user_language: str):
    i18n = I18n(user_language)
    
    await message.answer(
        i18n("choose_language"),
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: types.CallbackQuery, db_user, user_language: str):
    # Получаем выбранный язык
    selected_lang = callback.data.split("_")[1]  # ru, en, cs
    
    # Обновляем язык в базе данных
    await update_user_language(db_user.id, selected_lang)
    
    # Создаем i18n для нового языка для подтверждения
    i18n = I18n(selected_lang)
    
    # Убираем инлайн кнопки и отправляем подтверждение
    await callback.message.edit_text(
        i18n("language_changed"),
        reply_markup=None
    )
    
    await callback.answer()
