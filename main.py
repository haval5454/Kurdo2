import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = '8725595567:AAG1lw-AMx0v9EQS_i9fsFPn5QcFi8zHaSc'

# خەزنکردنی دۆخی لینک سڕینەوە لە memory
delete_links_status = {} 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "بۆتی هاوکاری گروپ - یەکێک هەڵبژێرە:"
    keyboard = [
        [InlineKeyboardButton("سڕینەوەی لینکەکان 🖇️", callback_data='delete_links_confirm')],
        [InlineKeyboardButton("لە گروپەکەم زیادم بکە ➕", url="https://t.me/parezraw_bot?startgroup=true")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()

    if query.data == 'delete_links_confirm':
        confirm_keyboard = [
            [InlineKeyboardButton("بەڵێ ✅", callback_data='enable'), InlineKeyboardButton("نەخێر ❌", callback_data='disable')]
        ]
        await query.edit_message_text("ئایا سڕینەوەی لینکەکان چالاک بکەم؟", reply_markup=InlineKeyboardMarkup(confirm_keyboard))

    elif query.data == 'enable':
        delete_links_status[chat_id] = True
        await query.edit_message_text("سڕینەوەی لینکەکان **چالاککرا** ✅")
    elif query.data == 'disable':
        delete_links_status[chat_id] = False
        await query.edit_message_text("سڕینەوەی لینکەکان **ناچالاککرا** ❌")

async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # پشکنین بۆ ئەوەی ئایا لەم گروپەدا چالاک کراوە
    if not delete_links_status.get(chat_id, False):
        return

    # پشکنینی ئەدمین
    user = update.message.from_user
    member = await context.bot.get_chat_member(chat_id, user.id)
    if member.status in ['creator', 'administrator']:
        return

    # ناسینەوەی لینک (هەم URL و هەم یوزەرنەیم)
    text = update.message.text or update.message.caption or ""
    link_pattern = r"https?://\S+|www\.\S+|t\.me/\S+|@\w+"
    
    if re.search(link_pattern, text):
        try:
            await update.message.delete()
        except Exception as e:
            print(f"ناتوانم پەیام بسڕمەوە: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    # فلتەری زیاتر بۆ دڵنیابوون لەوەی لینک دەگرێت
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, filter_links))
    app.run_polling()

if __name__ == '__main__':
    main()
    
