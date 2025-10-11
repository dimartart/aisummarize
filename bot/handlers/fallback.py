from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.services.i18n import I18n, get_user_language

router = Router()

@router.message()
async def fallback_message(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.language_code)
    i18n = I18n(lang)

    current_state = await state.get_state()
    if current_state:
        await message.answer(i18n("fallback_message_title"))
    else:
        await message.answer(i18n("fallback_message"))