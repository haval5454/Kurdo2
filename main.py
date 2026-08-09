import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = '8725595567:AAG1lw-AMx0v9EQS_i9fsFPn5QcFi8zHaSc'

# فەرمانی /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "✨ بەخێربێیت بۆ بۆتی هاوکاری گروپ! ✨\n\n"
        "ئەم بۆتە یارمەتیت دەدات بۆ بەڕێوەبردن و ڕێکخستنی گرووپەکەت بەبێ هیچ کێشەیەک.\n"
        "تکایە یەکێک لە هەڵبژاردنەکان هەڵبژێرە 👇"
    )

    keyboard = [
        [InlineKeyboardButton("سڕینەوەی هەموو لینکەکان 🖇️", callback_data='delete_links_confirm')],
        [InlineKeyboardButton("کات دانان بۆ ڤیدیۆ 🎬", callback_data='time_video')],
        [InlineKeyboardButton("کات دانان بۆ وێنە 🖼️", callback_data='time_image')],
        [InlineKeyboardButton("لە گروپەکەم زیادم بکە ➕", url="https://t.me/parezraw_bot?startgroup=true")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# بەڕێوەبردنی کلیکی دوگمەکان
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'delete_links_confirm':
        confirm_keyboard = [
            [
                InlineKeyboardButton("بەڵێ ✅", callback_data='enable_link_delete'),
                InlineKeyboardButton("نەخێر ❌", callback_data='disable_link_delete')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(confirm_keyboard)
        await query.edit_message_text(
            text="ئایا دڵنیایت لە چالاککردنی سڕینەوەی هەموو لینکەکان لە گروپدا؟",
            reply_markup=reply_markup
        )

    elif query.data == 'enable_link_delete':
        context.chat_data['delete_links'] = True
        await query.edit_message_text(text="سیستەمی سڕینەوەی لینکەکان بە سەرکەوتوویی **چالاککرا** ✅")

    elif query.data == 'disable_link_delete':
        context.chat_data['delete_links'] = False
        await query.edit_message_text(text="کردارەکە هەڵوەشێنرایەوە. سڕینەوەی لینکەکان **ناچالاکە** ❌")

# فلتەرکردن و سڕینەوەی پەیامەکان (جگە لە خاوەنی گروپ و ئەدمینەکان)
async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get('delete_links', False):
        if update.message and update.message.text:
            
            # پشکنین بۆ دەسەڵاتی نێرەری پەیامەکە
            chat_id = update.effective_chat.id
            user_id = update.message.from_user.id
            
            try:
                # وەرگرتنی زانیاری ئەندامەکە لە گروپدا
                member = await context.bot.get_chat_member(chat_id, user_id)
                
                # ئەگەر بەکارهێنەر خاوەنی گروپ (creator) یان ئەدمین (administrator) بێت، هیچ مەکە
                if member.status in ['creator', 'administrator']:
                    return
            except Exception as e:
                print(f"کێشە لە وەرگرتنی زانیاری ئەندام: {e}")

            # Regex ی ناسینەوەی لینکەکان بۆ ئەندامانی ئاسایی
            link_pattern = r"https?://\S+|www\.\S+|t\.me/\S+|@\w+"
            
            if re.search(link_pattern, update.message.text):
                try:
                    await update.message.delete()
                except Exception as e:
                    print(f"کێشە لە سڕینەوەی پەیام: {e}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # چاودێریکردنی پەیامەکان
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_links))

    print("بۆتەکە چالاک کرا...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
