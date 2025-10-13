from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.i18n import I18n

# Summarization level keyboard
def get_level_keyboard(i18n: I18n = None) -> InlineKeyboardMarkup:
    if i18n is None:
        i18n = I18n()
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=i18n("btn_short"), callback_data="level_short"),
            InlineKeyboardButton(text=i18n("btn_medium"), callback_data="level_medium"),
            InlineKeyboardButton(text=i18n("btn_details"), callback_data="level_details")
        ]
    ])

# Output format keyboard
def get_format_keyboard(i18n: I18n = None) -> InlineKeyboardMarkup:
    if i18n is None:
        i18n = I18n()
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=i18n("btn_message"), callback_data="format_message"),
            InlineKeyboardButton(text=i18n("btn_document"), callback_data="format_document")
        ]
    ])

# Создаем инлайн клавиатуру для выбора языка
def get_language_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton(text="🇨🇿 Čeština", callback_data="lang_cs")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)