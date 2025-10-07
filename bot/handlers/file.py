import os
from aiogram import Router, types, F
from bot.services.extractor import extract_text_from_file
from bot.services.gpt_client import summarize_text
from bot.config import settings

router = Router()

@router.message(F.document)
async def handle_document(message: types.Message):
    doc = message.document
    temp_path = os.path.join(settings.TEMP_DIR, doc.file_name)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)

    await message.answer("📥 Получил файл, извлекаю текст...")

    file = await message.bot.get_file(doc.file_id)
    await message.bot.download_file(file.file_path, temp_path)

    text = extract_text_from_file(temp_path)
    if not text:
        await message.answer("⚠️ Не удалось извлечь текст из файла.")
        return

    await message.answer("🧠 Сжимаю документ, подожди немного...")
    summary = summarize_text(text)
    await message.answer(f"📘 Конспект готов:\n\n{summary[:4000]}")

    os.remove(temp_path)
