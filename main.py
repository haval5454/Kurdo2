import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = '8725595567:AAG1lw-AMx0v9EQS_i9fsFPn5QcFi8zHaSc'

# خەزنکردنی دۆخی لینک سڕینەوە بۆ هەر گروپێک بە جیا
delete_links_status = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("سڕینەوەی لینکەکان 🖇️", callback_data='menu_links')],
        [InlineKeyboardButton("لە گروپەکەم زیادم بکە ➕", url="https://t.me/parezraw_bot?startgroup=true")]
    ]
    await update.message.reply_text("فەرموو، هەڵبژاردنەکەت بکە:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()

    if query.data == 'menu_links':
        kb = [[InlineKeyboardButton("بەڵێ، چالاکی بکە ✅", callback_data='enable'), 
               InlineKeyboardButton("نەخێر ❌", callback_data='disable')]]
        await query.edit_message_text("ئایا دڵنیایت لینکەکان بسڕمەوە؟", reply_markup=InlineKeyboardMarkup(kb))
    
    elif query.data == 'enable':
        delete_links_status[chat_id] = True
        await query.edit_message_text("سڕینەوەی لینکەکان بۆ ئەم گروپە **چالاککرا** ✅")
    elif query.data == 'disable':
        delete_links_status[chat_id] = False
        await query.edit_message_text("سڕینەوەی لینکەکان **ناچالاککرا** ❌")

async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    chat_id = update.effective_chat.id
    
    # ئەگەر لەم گروپەدا چالاک نەکرابوو، هیچی مەکە
    if not delete_links_status.get(chat_id, False):
        return

    # پشکنینی ئەدمین (ئەگەر ئەدمین بوو، با لینک بنێرێت)
    try:
        user = update.message.from_user
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in ['creator', 'administrator']:
            return
    except:
        pass

    # پشکنینی دەق یان کاپشن
    text = (update.message.text or "") + (update.message.caption or "")
    
    # ئەمەش Regex کە هەموو جۆرەکانی دەگرێت
    # t.me/ یان لینک یان www یان https یان @username
    pattern = r"(https?://\S+|www\.\S+|t\.me/\S+|@\w+)"
    
    if re.search(pattern, text):
        try:
            await update.message.delete()
            print(f"پەیامێکی لینک سڕدرایەوە لە گروپ: {chat_id}")
        except Exception as e:
            print(f"هەڵە لە سڕینەوە: {e} (تکایە دڵنیابە بۆتەکە ئەدمینە)")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # چاودێریکردنی هەموو پەیامەکان (Text + Caption)
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, filter_links))
    
    print("بۆتەکە چالاکە...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
