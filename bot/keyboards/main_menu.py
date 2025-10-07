from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📄 Загрузить файл")],
        [KeyboardButton(text="🔗 Вставить ссылку")],
    ],
    resize_keyboard=True
)