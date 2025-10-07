from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Summarization level keyboard
def get_level_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Short", callback_data="level_short"),
            InlineKeyboardButton(text="Medium", callback_data="level_medium"),
            InlineKeyboardButton(text="In Details", callback_data="level_details")
        ]
    ])

# Output format keyboard
def get_format_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Message", callback_data="format_message"),
            InlineKeyboardButton(text="Document", callback_data="format_document")
        ]
    ])

