import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = "8725595567:AAG1lw-AMx0v9EQS_i9fsFPn5QcFi8zHaSc"

# گرووپەکانی کە پاراستنی لینک لێیان چالاکە
link_protection = set()


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "➕ لە گروپەکەت زیادم بکە",
                url="https://t.me/parezraw_bot?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                "1️⃣ کات بۆ سڕینەوەی ڤیدیۆکان",
                callback_data="video"
            )
        ],
        [
            InlineKeyboardButton(
                "2️⃣ کات دانان بۆ سڕینەوەی وێنەکان",
                callback_data="photo"
            )
        ],
        [
            InlineKeyboardButton(
                "3️⃣ سڕینەوەی هەموو لینکەکان",
                callback_data="links"
            )
        ]
    ]

    await update.message.reply_text(
        "✨ بەخێربێیت ✨\n\n"
        "👇 هەڵبژاردنێک هەڵبژێرە:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# Button Handler
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    # =========================
    # سڕینەوەی لینکەکان
    # =========================

    if query.data == "links":

        keyboard = [
            [
                InlineKeyboardButton(
                    "بەڵێ ✅",
                    callback_data="yes_links"
                ),
                InlineKeyboardButton(
                    "نەخێر ❌",
                    callback_data="no_links"
                )
            ]
        ]

        await query.edit_message_text(
            "ڕازیت؟\n\n"
            "هەر پەیامێک لینک یان @username ـی تێدا بێت "
            "لە گرووپەکە دەسڕێتەوە.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # =========================
    # بەڵێ
    # =========================

    elif query.data == "yes_links":

        if query.message.chat.type in ["group", "supergroup"]:

            chat_id = query.message.chat.id

            link_protection.add(chat_id)

            await query.edit_message_text(
                "✅ سڕینەوەی لینکەکان چالاک کرا.\n\n"
                "لە ئێستاوە هەر پەیامێک کە "
                "لینک یان @username ـی تێدا بێت "
                "لەو گرووپە دەسڕێتەوە."
            )

        else:

            await query.edit_message_text(
                "⚠️ ئەم هەڵبژاردنە دەبێت لە گرووپەکە چالاک بکرێت."
            )

    # =========================
    # نەخێر
    # =========================

    elif query.data == "no_links":

        await query.edit_message_text(
            "❌ سڕینەوەی لینکەکان چالاک نەکرا."
        )


# =========================
# Link / Username Detector
# =========================

async def delete_links(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.effective_message
    chat = update.effective_chat

    if not message or not chat:
        return

    # تەنها گرووپە چالاککراوەکان
    if chat.id not in link_protection:
        return

    # دەقی پەیام یان caption
    text = message.text or message.caption or ""

    # پشکنینی:
    # http://
    # https://
    # www.
    # t.me/
    # @username
    pattern = r"(https?://\S+|www\.\S+|t\.me/\S+|@\w+)"

    if re.search(pattern, text, re.IGNORECASE):

        try:
            await message.delete()

        except Exception as e:
            print(f"Could not delete message: {e}")


# =========================
# Main
# =========================

def main():

    app = Application.builder().token(TOKEN).build()

    # /start
    app.add_handler(
        CommandHandler("start", start)
    )

    # دوگمەکان
    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # پشکنینی پەیامەکان بۆ لینک و @
    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.CAPTION,
            delete_links
        )
    )

    print("Bot is running...")

    app.run_polling()


# =========================
# Run
# =========================

if __name__ == "__main__":
    main()
