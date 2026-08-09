from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# تۆکنی بۆتەکەت لێرە دابنێ
TOKEN = '8725595567:AAG1lw-AMx0v9EQS_i9fsFPn5QcFi8zHaSc'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # دەقی پەیامەکە
    text = (
        "✨ بەخێربێیت بۆ بۆتی هاوکاری گروپ! ✨\n\n"
        "ئەم بۆتە یارمەتیت دەدات بۆ بەڕێوەبردن و ڕێکخستنی گرووپەکەت بەبێ هیچ کێشەیەک.\n"
        "تکایە یەکێک لە هەڵبژاردنەکان هەڵبژێرە 👇"
    )

    # دروستکردنی دوگمەکان (Inline Keyboards)
    keyboard = [
        [InlineKeyboardButton("سڕینەوەی هەموو لینکەکان 🖇️", callback_data='delete_links')],
        [InlineKeyboardButton("کات دانان بۆ ڤیدیۆ 🎬", callback_data='time_video')],
        [InlineKeyboardButton("کات دانان بۆ وێنە 🖼️", callback_data='time_image')],
        [InlineKeyboardButton("لە گروپەکەم زیادم بکە ➕", url="https://t.me/parezraw_bot?startgroup=true")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    # ناردنی پەیامەکە
    await update.message.reply_text(text, reply_markup=reply_markup)

def main():
    app = Application.builder().token(TOKEN).build()

    # کاتێک بەکارهێنەر داوای /start دەکات
    app.add_handler(CommandHandler("start", start))

    print("بۆتەکە چالاک کرا...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
