from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

BUTTON_REGEX = re.compile(r"\[([^\]]+)\]\(buttonurl:(.+?)\)")


# =========================
# PARSE BUTTONS (DB SAFE)
# =========================
def parse_buttons(text: str):
    """
    Extract buttons from text.
    Returns LIST of button dicts (DB safe).
    """
    if not text:
        return None

    buttons = []

    for line in text.split("\n"):
        match = BUTTON_REGEX.search(line)
        if match:
            label = match.group(1)
            url = match.group(2)
            buttons.append(
                {
                    "text": label,
                    "url": url
                }
            )

    return buttons if buttons else None


# =========================
# BUILD MARKUP (RUNTIME)
# =========================
def build_keyboard(buttons):
    """
    Convert DB button data to InlineKeyboardMarkup
    """
    if not buttons:
        return None

    keyboard = []
    for btn in buttons:
        keyboard.append([
            InlineKeyboardButton(
                text=btn["text"],
                url=btn["url"]
            )
        ])

    return InlineKeyboardMarkup(keyboard)
