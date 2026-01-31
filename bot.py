import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("❌ BOT_TOKEN غير موجود. تأكد من إضافة المتغير في Railway.")

user_wheel = {}

# ==================== HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_wheel:
        user_wheel[user_id] = {"items": [], "active": False}
    keyboard = [
        [InlineKeyboardButton("إنهاء وتجهيز العجلة", callback_data="finish_wheel")],
        [InlineKeyboardButton("تغيير الأسئلة", callback_data="reset_wheel")]
    ]
    await update.message.reply_text(
        "أرسل لي كل سؤال أو صورة على حدى.\nبعد الانتهاء اضغط أحد الأزرار:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def receive_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_wheel:
        await update.message.reply_text("اضغط /start أولاً لتجهيز العجلة.")
        return

    item = None
    if update.message.text:
        item = {"type": "text", "content": update.message.text}
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        item = {"type": "photo", "content": file_id}

    if item:
        user_wheel[user_id]["items"].append(item)
        await update.message.reply_text(f"تم إضافة عنصر جديد. العدد الحالي: {len(user_wheel[user_id]['items'])}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "finish_wheel":
        if user_id not in user_wheel or not user_wheel[user_id]["items"]:
            await query.edit_message_text("لم تقم بإضافة أي عناصر بعد.")
            return
        random.shuffle(user_wheel[user_id]["items"])
        user_wheel[user_id]["active"] = True
        await query.edit_message_text("تم تجهيز العجلة بنجاح! جاهزة للاستخدام في المجموعة.")

    elif query.data == "reset_wheel":
        user_wheel[user_id] = {"items": [], "active": False}
        await query.edit_message_text("تم مسح جميع العناصر. يمكنك البدء بإضافة عناصر جديدة.")

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_wheel or not user_wheel[user_id]["active"]:
        await update.message.reply_text("العجلة غير مفعلة أو لم يتم تجهيزها بعد في المحادثة الخاصة.")
        return

    item = random.choice(user_wheel[user_id]["items"])
    if item["type"] == "text":
        await update.message.reply_text(f"🎡 العجلة توقفت على:\n{item['content']}")
    elif item["type"] == "photo":
        await update.message.reply_photo(photo=item["content"], caption="🎡 العجلة توقفت على صورة!")

# ==================== MAIN ====================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, receive_item))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(CommandHandler("spin", spin))

print("✅ البوت بدأ بنجاح")
app.run_polling()
