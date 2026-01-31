import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv

# تحميل توكن البوت من ملف .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# تخزين العناصر لكل مستخدم (أسئلة أو صور)
user_wheel = {}  # user_id: {"items": [], "active": False}

# بدء المحادثة الخاصة
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_wheel:
        user_wheel[user_id] = {"items": [], "active": False}
    keyboard = [
        [InlineKeyboardButton("إنهاء وتجهيز العجلة", callback_data="finish_wheel")],
        [InlineKeyboardButton("تغيير الأسئلة", callback_data="reset_wheel")]
    ]
    update.message.reply_text(
        "أرسل لي كل سؤال أو صورة على حدى.\nبعد الانتهاء اضغط أحد الأزرار:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# استقبال النصوص أو الصور
def receive_item(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_wheel:
        update.message.reply_text("اضغط /start أولاً لتجهيز العجلة.")
        return
    
    item = None
    if update.message.text:
        item = {"type": "text", "content": update.message.text}
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        item = {"type": "photo", "content": file_id}
    
    if item:
        user_wheel[user_id]["items"].append(item)
        update.message.reply_text(f"تم إضافة عنصر جديد. العدد الحالي: {len(user_wheel[user_id]['items'])}")

# التعامل مع أزرار إنهاء أو إعادة ضبط العجلة
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    
    if query.data == "finish_wheel":
        if user_id not in user_wheel or not user_wheel[user_id]["items"]:
            query.edit_message_text("لم تقم بإضافة أي عناصر بعد.")
            return
        random.shuffle(user_wheel[user_id]["items"])
        user_wheel[user_id]["active"] = True
        query.edit_message_text("تم تجهيز العجلة بنجاح! جاهزة للاستخدام في المجموعة.")
    
    elif query.data == "reset_wheel":
        user_wheel[user_id] = {"items": [], "active": False}
        query.edit_message_text("تم مسح جميع العناصر. يمكنك البدء بإضافة عناصر جديدة.")

# دوران العجلة في المجموعة
def spin(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_wheel or not user_wheel[user_id]["active"]:
        update.message.reply_text("العجلة غير مفعلة أو لم يتم تجهيزها بعد في المحادثة الخاصة.")
        return
    
    item = random.choice(user_wheel[user_id]["items"])
    
    if item["type"] == "text":
        update.message.reply_text(f"🎡 العجلة توقفت على:\n{item['content']}")
    elif item["type"] == "photo":
        update.message.reply_photo(photo=item["content"], caption="🎡 العجلة توقفت على صورة!")

# إعداد البوت
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text | Filters.photo, receive_item))
dispatcher.add_handler(CallbackQueryHandler(button_handler))
dispatcher.add_handler(CommandHandler('spin', spin))  # يستخدم في المجموعة

updater.start_polling()
updater.idle()
