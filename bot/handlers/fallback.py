from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.services.i18n import I18n

router = Router()

@router.message()
async def fallback_message(message: types.Message, state: FSMContext, user_language: str):
    i18n = I18n(user_language)

    current_state = await state.get_state()
    if current_state:
        await message.answer(i18n("fallback_message_title"))
    else:
        await message.answer(i18n("fallback_message"))