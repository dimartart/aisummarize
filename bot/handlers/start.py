from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states import SummarizeStates
from bot.keyboards.inline_keyboards import get_level_keyboard, get_format_keyboard
import os
import asyncio
from bot.services.extractor import extract_text_from_file
from bot.services.gpt_client import summarize_text
from bot.config import settings
from datetime import datetime

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    text = "Hello, I am AI assistant that can summarize content of PDF and Word files. Send me the Word/PDF/youtube link for summarization"
    await message.answer(text)
    await state.set_state(SummarizeStates.waiting_for_file)

# Handle document input
@router.message(SummarizeStates.waiting_for_file, F.document)
async def handle_document(message: types.Message, state: FSMContext):
    doc = message.document
    file_name = doc.file_name.lower()
    
    # Check if it's PDF or Word
    if not (file_name.endswith('.pdf') or file_name.endswith('.docx') or file_name.endswith('.doc')):
        await message.answer("Please send me PDF or word file")
        return
    
    # Save file info to state
    await state.update_data(
        file_id=doc.file_id,
        file_name=doc.file_name,
        file_path=None
    )
    
    await message.answer("Ok, than choose how much should I summarize", reply_markup=get_level_keyboard())
    await state.set_state(SummarizeStates.waiting_for_level)

# Handle wrong input when waiting for file
@router.message(SummarizeStates.waiting_for_file)
async def handle_wrong_file(message: types.Message):
    await message.answer("Please send me PDF or word file")

# Handle level selection
@router.callback_query(SummarizeStates.waiting_for_level, F.data.startswith("level_"))
async def handle_level_selection(callback: types.CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]  # short, medium, details
    await state.update_data(level=level)
    
    await callback.message.edit_text("Ok, than choose how much should I summarize\n✓ Selected: " + level.capitalize())
    await callback.message.answer("Summarization in progress... if your file is big summarization can take up to 5 minutes")
    
    await state.set_state(SummarizeStates.processing)
    
    # Create async task for summarization
    asyncio.create_task(process_summarization(callback.message, state))
    await callback.answer()

# Handle wrong input when waiting for level
@router.message(SummarizeStates.waiting_for_level)
async def handle_wrong_level(message: types.Message):
    await message.answer("Ok, than choose how much should I summarize", reply_markup=get_level_keyboard())

# Process summarization in background
async def process_summarization(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        file_id = data['file_id']
        file_name = data['file_name']
        level = data['level']
        
        # Download file
        file = await message.bot.get_file(file_id)
        temp_path = os.path.join(settings.TEMP_DIR, f"{datetime.now().timestamp()}_{file_name}")
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        
        await message.bot.download_file(file.file_path, temp_path)
        
        # Extract text
        text = extract_text_from_file(temp_path)
        if not text:
            await message.answer("⚠️ Failed to extract text from file. Please try another file.")
            await state.clear()
            return
        
        # Summarize
        summary = await summarize_text(text, level)
        
        # Save summary to state
        await state.update_data(summary=summary, temp_file_path=temp_path)
        
        # Ask for format
        await message.answer(
            "Your summarization is done. Do you want result as message or document?",
            reply_markup=get_format_keyboard()
        )
        await state.set_state(SummarizeStates.waiting_for_format)
        
    except Exception as e:
        print(f"Error in summarization: {e}")
        await message.answer("⚠️ Error during summarization. Please try again.")
        await state.clear()

# Handle wrong input during processing
@router.message(SummarizeStates.processing)
async def handle_wrong_processing(message: types.Message):
    await message.answer("Summarization in progress... if your file is big summarization can take up to 5 minutes")

# Handle format selection
@router.callback_query(SummarizeStates.waiting_for_format, F.data.startswith("format_"))
async def handle_format_selection(callback: types.CallbackQuery, state: FSMContext):
    format_type = callback.data.split("_")[1]  # message or document
    data = await state.get_data()
    summary = data['summary']
    temp_file_path = data.get('temp_file_path')
    
    await callback.message.edit_text("Your summarization is done. Do you want result as message or document?\n✓ Selected: " + format_type.capitalize())
    
    if format_type == "message":
        # Send as text message
        if len(summary) > 4096:
            # Split into multiple messages if too long
            for i in range(0, len(summary), 4096):
                await callback.message.answer(summary[i:i+4096])
        else:
            await callback.message.answer(f"Here your summarization!\n\n{summary}")
    else:
        # Send as document
        summary_file = os.path.join(settings.TEMP_DIR, f"summary_{datetime.now().timestamp()}.txt")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        with open(summary_file, 'rb') as f:
            await callback.message.answer_document(
                types.BufferedInputFile(f.read(), filename="summary.txt"),
                caption="Here your summarization!"
            )
        
        # Clean up summary file
        if os.path.exists(summary_file):
            os.remove(summary_file)
    
    # Clean up temp file
    if temp_file_path and os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    
    # Return to initial state
    await state.clear()
    await callback.message.answer("Send me another file to summarize or use /start")
    await callback.answer()

# Handle wrong input when waiting for format
@router.message(SummarizeStates.waiting_for_format)
async def handle_wrong_format(message: types.Message):
    await message.answer(
        "Your summarization is done. Do you want result as message or document?",
        reply_markup=get_format_keyboard()
    )
