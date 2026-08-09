import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    filters,
)

TOKEN = "BOT_TOKEN"

# گرووپەکان کە بۆتەکە تێیانە
bot_groups = {}

# گرووپەکانی کە سڕینەوەی لینک لێیان چالاکە
link_protection = set()


# =========================================================
# /start
# =========================================================

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
        ],
    ]

    text = """
✨ بەخێربێیت ✨

👇 یەکێک لە هەڵبژاردنەکان هەڵبژێرە:
"""

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# دوگمەکان
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    # -----------------------------------------------------
    # سڕینەوەی لینکەکان
    # -----------------------------------------------------

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
                ),
            ]
        ]

        await query.edit_message_text(
            "ڕازیت؟\n\n"
            "هەر پەیامێک لینک یان @username ـی تێدا بێت "
            "لە گرووپەکە دەسڕێتەوە.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # -----------------------------------------------------
    # بەڵێ
    # -----------------------------------------------------

    elif query.data == "yes_links":

        # تەنها Private Chat
        if query.message.chat.type != "private":
            await query.edit_message_text(
                "⚠️ تکایە ئەم کارە لە Private Chat ـی بۆتەکە بکە."
            )
            return

        # ئەگەر هیچ گرووپێک نەدۆزرایەوە
        if not bot_groups:

            await query.edit_message_text(
                "⚠️ هیچ گرووپێک نەدۆزرایەوە.\n\n"
                "سەرەتا بۆتەکە زیاد بکە بۆ گرووپەکەت و "
                "بیکە بە Admin."
            )
            return

        # پیشاندانی گرووپەکان
        keyboard = []

        for chat_id, chat_title in bot_groups.items():

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"📌 {chat_title}",
                        callback_data=f"select_group:{chat_id}"
                    )
                ]
            )

        await query.edit_message_text(
            "📌 گرووپەکە هەڵبژێرە:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # -----------------------------------------------------
    # نەخێر
    # -----------------------------------------------------

    elif query.data == "no_links":

        await query.edit_message_text(
            "❌ هەڵوەشێنرایەوە."
        )

    # -----------------------------------------------------
    # هەڵبژاردنی گرووپ
    # -----------------------------------------------------

    elif query.data.startswith("select_group:"):

        chat_id = int(
            query.data.split(":")[1]
        )

        if chat_id not in bot_groups:

            await query.edit_message_text(
                "⚠️ ئەم گرووپە نەدۆزرایەوە."
            )
            return

        link_protection.add(chat_id)

        group_name = bot_groups[chat_id]

        await query.edit_message_text(
            f"✅ سڕینەوەی لینکەکان چالاک کرا.\n\n"
            f"📌 گرووپ: {group_name}\n\n"
            "لە ئێستاوە هەر پەیامێک کە "
            "لینک یان @username ـی تێدا بێت "
            "لەو گرووپە دەسڕێتەوە."
        )


# =========================================================
# دۆزینەوەی گرووپ کاتێک بۆتەکە زیاد دەکرێت
# =========================================================

async def bot_added_to_group(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_member = update.my_chat_member

    if not chat_member:
        return

    chat = chat_member.chat

    new_status = chat_member.new_chat_member.status

    # بۆتەکە بوو بە member/admin
    if new_status in ["member", "administrator"]:

        if chat.type in ["group", "supergroup"]:

            bot_groups[chat.id] = chat.title or "بێ ناو"


# =========================================================
# سڕینەوەی لینک و @username
# =========================================================

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

    text = message.text or message.caption or ""

    # دۆزینەوەی:
    # http://
    # https://
    # www.
    # t.me/
    # @username

    pattern = r"(https?://\S+|www\.\S+|t\.me/\S+|@\w+)"

    if re.search(pattern, text, re.IGNORECASE):

        try:
            await message.delete()

        except Exception as error:

            print(
                f"Could not delete message: {error}"
            )


# =========================================================
# Main
# =========================================================

def main():

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # دوگمەکان
    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # کاتێک بۆتەکە زیاد دەکرێت بۆ گرووپ
    app.add_handler(
        ChatMemberHandler(
            bot_added_to_group,
            ChatMemberHandler.MY_CHAT_MEMBER
        )
    )

    # پشکنینی پەیامەکان
    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.CAPTION,
            delete_links
        )
    )

    print("🤖 Bot is running...")

    app.run_polling()


# =========================================================
# Run
# =========================================================

if __name__ == "__main__":
    main()
