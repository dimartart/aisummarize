from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from bot.services.i18n import I18n, get_user_language

router = Router()

@router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    # Get user language for localized response
    lang = get_user_language(message.from_user.language_code)
    i18n = I18n(lang)

    # Clear state
    await state.clear()
    
    # Send localized cancel message
    await message.answer(i18n("action_canceled"))