import asyncio
import logging
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

TOKEN = "8725595567:AAG1lw-AMx0v9EQS_i9fsFPn5QcFi8zHaSc"
ADMIN_ID = 8734106005

DELETE_DELAY = 900
PHOTO_DELETE_DELAY = 10800  # 3 hours

URL_REGEX = re.compile(
    r'(https?://\S+|t\.me/\S+|www\.\S+|@\w+)',
    re.IGNORECASE
)

logging.basicConfig(level=logging.INFO)

# هەڵبژاردنی سڕینەوەی لینک بۆ هەر گرووپێک جیاوازە
link_protection = {}


async def delete_msg(bot, chat_id, msg_id):
    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=msg_id
        )
    except:
        pass


async def delete_photo(bot, chat_id, msg_id):
    await asyncio.sleep(PHOTO_DELETE_DELAY)

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=msg_id
        )
    except:
        pass


async def process_media(
    bot,
    chat_id,
    msg_id,
    file_id,
    caption,
    is_video=True
):
    await asyncio.sleep(DELETE_DELAY)

    await delete_msg(
        bot,
        chat_id,
        msg_id
    )

    try:
        if is_video:
            await bot.send_video(
                ADMIN_ID,
                video=file_id,
                caption=caption
            )
        else:
            await bot.send_animation(
                ADMIN_ID,
                animation=file_id,
                caption=caption
            )
    except:
        pass


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "1️⃣ کات دانان بۆ سڕینەوەی ڤیدیۆکان",
                callback_data="video_settings"
            )
        ],
        [
            InlineKeyboardButton(
                "2️⃣ کات دانان بۆ سڕینەوەی وێنەکان",
                callback_data="photo_settings"
            )
        ],
        [
            InlineKeyboardButton(
                "3️⃣ سڕینەوەی هەموو لینکێک",
                callback_data="link_settings"
            )
        ]
    ]

    await update.message.reply_text(
        """✨ بەخێربێیت بۆ بۆتی هاوکاری گروپ! ✨

ئەم بۆتە یارمەتیت دەدات بۆ بەڕێوەبردن و ڕێکخستنی گرووپەکەت بەبێ هیچ کێشەیەک.

بەشە سەرەکییەکانی:
1- کات دانان بۆ سڕینەوەی ڤیدیۆکان
2- کات دانان بۆ سڕینەوەی وێنەکان
3- سڕینەوەی هەموو لینکێک

تکایە یەکێک لە هەڵبژاردنەکان هەڵبژێرە 👇""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# دوگمەکان
async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id

    # بەشی لینکەکان
    if query.data == "link_settings":

        keyboard = [
            [
                InlineKeyboardButton(
                    "بەڵێ ✅",
                    callback_data="links_on"
                ),
                InlineKeyboardButton(
                    "نەخێر ❌",
                    callback_data="links_off"
                )
            ]
        ]

        await query.message.reply_text(
            "🔗 ئایا دڵنیایت دەتەوێت سڕینەوەی هەموو لینکەکان چالاک بکەیت؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # چالاککردنی لینک
    elif query.data == "links_on":

        link_protection[chat_id] = True

        await query.message.reply_text(
            "✅ سڕینەوەی لینکەکان چالاک کرا.\n\n"
            "لە ئێستاوە هەر لینکێک لەم گرووپەدا بنێردرێت دەسڕێتەوە."
        )

    # ناچالاککردنی لینک
    elif query.data == "links_off":

        link_protection[chat_id] = False

        await query.message.reply_text(
            "❌ سڕینەوەی لینکەکان ناچالاک کرا.\n\n"
            "لینکەکان لەم گرووپەدا ناسڕێنەوە."
        )

    # ئەمانە هێشتا کاریان زیاد نەکراوە
    elif query.data == "video_settings":

        await query.message.reply_text(
            "🎥 بەشی کات دانان بۆ سڕینەوەی ڤیدیۆکان دواتر زیاد دەکرێت."
        )

    elif query.data == "photo_settings":

        await query.message.reply_text(
            "🖼️ بەشی کات دانان بۆ سڕینەوەی وێنەکان دواتر زیاد دەکرێت."
        )


async def handle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    msg = update.message

    if not msg:
        return

    text = msg.text or msg.caption or ""

    # 🔗 تەنها ئەگەر بۆ ئەم گرووپە سڕینەوەی لینک چالاک کرابێت
    if link_protection.get(msg.chat_id, False):

        if URL_REGEX.search(text):

            await delete_msg(
                context.bot,
                msg.chat_id,
                msg.message_id
            )

            return

    # 🤖 block ONLY bot text messages
    if msg.text and msg.from_user and msg.from_user.is_bot:

        await delete_msg(
            context.bot,
            msg.chat_id,
            msg.message_id
        )

        return

    # 🎥 video
    if msg.video:

        asyncio.create_task(
            process_media(
                context.bot,
                msg.chat_id,
                msg.message_id,
                msg.video.file_id,
                msg.caption,
                True
            )
        )

    # 🎞 GIF / animation
    elif msg.animation:

        asyncio.create_task(
            process_media(
                context.bot,
                msg.chat_id,
                msg.message_id,
                msg.animation.file_id,
                msg.caption,
                False
            )
        )

    # 🖼 photo
    elif msg.photo:

        asyncio.create_task(
            delete_photo(
                context.bot,
                msg.chat_id,
                msg.message_id
            )
        )


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # /start
    app.add_handler(
        CommandHandler("start", start)
    )

    # دوگمەکان
    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # پەیامەکان
    app.add_handler(
        MessageHandler(filters.ALL, handle)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
