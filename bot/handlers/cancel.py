from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from bot.services.i18n import I18n
from bot.states import SummarizeStates
from bot.utils.task_manager import cancel_task

router = Router()

@router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext, user_language: str):
    i18n = I18n(user_language)
    
    user_id = message.from_user.id
    
    # Cancel active task if any
    cancel_task(user_id)
    
    # Check for temp file in state and clean it up
    try:
        data = await state.get_data()
        temp_file_path = data.get('temp_file_path')
        if temp_file_path:
            from bot.utils.task_manager import cleanup_temp_file
            cleanup_temp_file(temp_file_path)
    except Exception as e:
        print(f"Error cleaning up temp file during cancel: {e}")
    
    # Clear state
    await state.clear()
    
    # Set to initial state for new file upload
    await state.set_state(SummarizeStates.waiting_for_file)
    
    # Send localized cancel message
    await message.answer(i18n("action_canceled"))