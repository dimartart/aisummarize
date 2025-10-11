from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states import SummarizeStates
from bot.keyboards.inline_keyboards import get_level_keyboard, get_format_keyboard
import os
import asyncio
from bot.services.extractor import extract_text_from_file
from bot.services.gpt_client import summarize_text
from bot.services.document_generator import create_docx, create_pdf
from bot.services.i18n import I18n, get_user_language
from bot.config import settings
from datetime import datetime

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Get user language
    lang = get_user_language(message.from_user.language_code)
    await state.update_data(language=lang)
    
    i18n = I18n(lang)
    await message.answer(i18n("start_message"))
    await state.set_state(SummarizeStates.waiting_for_file)

# Handle document input
@router.message(SummarizeStates.waiting_for_file, F.document)
async def handle_document(message: types.Message, state: FSMContext):
    doc = message.document
    file_name = doc.file_name.lower()
    
    # Get user language
    data = await state.get_data()
    i18n = I18n(data.get('language', 'en'))
    
    # Check if it's PDF or Word
    if not (file_name.endswith('.pdf') or file_name.endswith('.docx') or file_name.endswith('.doc')):
        await message.answer(i18n("please_send_file"))
        return
    
    # Determine file type
    if file_name.endswith('.pdf'):
        file_type = 'pdf'
    else:
        file_type = 'docx'
    
    # Save file info to state
    await state.update_data(
        file_id=doc.file_id,
        file_name=doc.file_name,
        file_path=None,
        file_type=file_type
    )
    
    await message.answer(i18n("choose_level"), reply_markup=get_level_keyboard(i18n))
    await state.set_state(SummarizeStates.waiting_for_level)

# Handle level selection
@router.callback_query(SummarizeStates.waiting_for_level, F.data.startswith("level_"))
async def handle_level_selection(callback: types.CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]  # short, medium, details
    await state.update_data(level=level)
    
    # Get user language
    data = await state.get_data()
    i18n = I18n(data.get('language', 'en'))
    
    await callback.message.edit_text(
        f"{i18n('choose_level')}\n{i18n('selected')} {i18n('btn_' + level).capitalize()}",
        reply_markup=None
    )
    await callback.message.answer(i18n("processing"))
    
    await state.set_state(SummarizeStates.processing)
    
    # Create async task for summarization
    asyncio.create_task(process_summarization(callback.message, state))


    await callback.answer()

# Process summarization in background
async def process_summarization(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        file_id = data['file_id']
        file_name = data['file_name']
        level = data['level']
        i18n = I18n(data.get('language', 'en'))
        
        # Download file
        file = await message.bot.get_file(file_id)
        temp_path = os.path.join(settings.TEMP_DIR, f"{datetime.now().timestamp()}_{file_name}")
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        
        await message.bot.download_file(file.file_path, temp_path)
        
        # Extract text
        text = extract_text_from_file(temp_path)
        if not text:
            await message.answer(i18n("extraction_failed"))
            await state.clear()
            return
        
        # Summarize
        summary = await summarize_text(text, level)
        
        # Save summary to state
        await state.update_data(summary=summary, temp_file_path=temp_path)
        
        # Ask for format
        await message.answer(
            i18n("choose_format"),
            reply_markup=get_format_keyboard(i18n)
        )
        await state.set_state(SummarizeStates.waiting_for_format)
        
    except Exception as e:
        print(f"Error in summarization: {e}")
        data = await state.get_data()
        i18n = I18n(data.get('language', 'en'))
        await message.answer(i18n("error_summarization"))
        await state.clear()

# Handle format selection
@router.callback_query(SummarizeStates.waiting_for_format, F.data.startswith("format_"))
async def handle_format_selection(callback: types.CallbackQuery, state: FSMContext):
    format_type = callback.data.split("_")[1]  # message or document
    data = await state.get_data()
    summary = data['summary']
    temp_file_path = data.get('temp_file_path')
    file_type = data.get('file_type', 'txt')  # Get original file type
    i18n = I18n(data.get('language', 'en'))
    
    await callback.message.edit_text(
        f"{i18n('choose_format')}\n{i18n('selected')} {i18n('btn_' + format_type).capitalize()}",
        reply_markup=None
    )
    
    if format_type == "message":
        # Send as text message
        if len(summary) > 4096:
            # Split into multiple messages if too long
            for i in range(0, len(summary), 4096):
                await callback.message.answer(summary[i:i+4096])
        else:
            await callback.message.answer(f"{i18n('here_summary')}\n\n{summary}")
    else:
        # Send as document in the same format as input
        summary_file = None
        
        if file_type == 'pdf':
            # Create PDF
            summary_file = os.path.join(settings.TEMP_DIR, f"summary_{datetime.now().timestamp()}.pdf")
            create_pdf(summary, summary_file)
            filename = "summary.pdf"
        elif file_type == 'docx':
            # Create Word document
            summary_file = os.path.join(settings.TEMP_DIR, f"summary_{datetime.now().timestamp()}.docx")
            create_docx(summary, summary_file)
            filename = "summary.docx"
        else:
            # Fallback to TXT
            summary_file = os.path.join(settings.TEMP_DIR, f"summary_{datetime.now().timestamp()}.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            filename = "summary.txt"
        
        with open(summary_file, 'rb') as f:
            await callback.message.answer_document(
                types.BufferedInputFile(f.read(), filename=filename),
                caption=i18n("here_summary")
            )
        
        # Clean up summary file
        if os.path.exists(summary_file):
            os.remove(summary_file)
    
    # Clean up temp file
    if temp_file_path and os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    
    # Return to initial state
    await state.clear()
    await callback.message.answer(i18n("send_another"))
    await callback.answer()