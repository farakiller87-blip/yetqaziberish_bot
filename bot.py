import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.environ.get("9076151422:AAEihOZQsVJLVnV4xtkgTyIjZUvaY_g-wj0")

# ========== RESTORANLAR + CLICK KARTALAR (TEST) ==========
RESTAURANTS = {
    "yashil": {
        "name": "Asl Burger Yashil Bozor",
        "admin_id": 6738827993,
        "address": "Farovon massivi, 109",
        "phone": "+998 99 588-13-30",
        "hours": "09:00 - 23:00",
        "click_card": "9860 1234 5678 9011",
        "click_name": "Asl Burger Yashil Bozor",
        "menu": {"Tandir Lavash": 38000, "Lavash Tovuq": 35000}
    },
    "daxa": {
        "name": "Asl Burger 5 Kichik Daxa",
        "admin_id": 8681088817,
        "address": "Alpomish, Alisher Navoiy 3G",
        "phone": "+998 99 588-13-30",
        "hours": "09:00 - 23:00",
        "click_card": "9860 1234 5678 9022",
        "click_name": "Asl Burger Daxa",
        "menu": {"Chizburger": 35000}
    }
}
DELIVERY = 15000
CHOOSING, ADDRESS, PHONE, PAYMENT, CLICK_SCREENSHOT = range(5)
users = {}

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot ishlayapti!"

def get_cafe_keyboard():
    kb = []
    for key, r in RESTAURANTS.items():
        kb.append([InlineKeyboardButton(r["name"], callback_data=f"cafe_{key}")])
    return InlineKeyboardMarkup(kb)

def build_order_text(u, r, first_name):
    total = sum(r["menu"][n]*c for n,c in u["cart"].items())
    text = f"🔥 *YANGI BUYURTMA!*\n\n🏪 Kafe: {r['name']}\n👤 Mijoz: {first_name}\n📞 Tel: {u.get('phone','')}\n📍 Manzil: {u.get('address','')}\n\n"
    for n,c in u["cart"].items():
        text += f"🛒 {n} x{c} - {r['menu'][n]*c} so'm\n"
    text += f"\n🚗 Yetkazib berish: {DELIVERY} so'm\n💰 *JAMI: {total+DELIVERY} so'm*\n"
    return text, total+DELIVERY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid] = {"cafe": None, "cart": {}}
    await update.message.reply_text("🍔 Qaysi kafedan buyurtma berasiz?", reply_markup=get_cafe_keyboard())
    return CHOOSING

async def choose_cafe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cafe_key = q.data.replace("cafe_", "")
    uid = q.from_user.id
    if uid not in users: users[uid] = {"cart": {}}
    users[uid]["cafe"] = cafe_key
    r = RESTAURANTS[cafe_key]
    text = f"🏪 *{r['name']}*\n📍 {r['address']}\n📞 {r['phone']}\n🕐 {r['hours']}\n\nMenyu:"
    kb = []
    for name, price in r["menu"].items():
        kb.append([InlineKeyboardButton(f"{name} - {price} so'm", callback_data=f"add_{name}")])
    kb.append([InlineKeyboardButton("🛒 Savat", callback_data="show_cart")])
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return CHOOSING

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("Savatga qo'shildi ✅")
    uid = q.from_user.id
    name = q.data.replace("add_", "")
    users[uid]["cart"][name] = users[uid]["cart"].get(name, 0) + 1
    return CHOOSING

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    u = users[uid]
    r = RESTAURANTS[u["cafe"]]
    if not u["cart"]:
        await q.edit_message_text("Savat bo'sh.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Menyuga", callback_data=f"cafe_{u['cafe']}")]]))
        return CHOOSING
    total = sum(r["menu"][n]*c for n,c in u["cart"].items())
    text = f"🛒 *Savat - {r['name']}*\n\n"
    for name, count in u["cart"].items():
        text += f"- {name} x{count} - {r['menu'][name]*count} so'm\n"
    text += f"\n🚗 Yetkazib berish: {DELIVERY} so'm\n💰 *Jami: {total+DELIVERY} so'm*"
    kb = [[InlineKeyboardButton("✅ Buyurtmani tasdiqlash", callback_data="checkout")],
          [InlineKeyboardButton("🗑 Tozalash", callback_data="clear")],
          [InlineKeyboardButton("⬅️ Menyuga", callback_data=f"cafe_{u['cafe']}")]]
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return CHOOSING

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    users[uid]["cart"] = {}
    await q.edit_message_text("Savat tozalandi", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Menyuga", callback_data=f"cafe_{users[uid]['cafe']}")]]))
    return CHOOSING

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("📍 Manzilni yozing:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid]["address"] = update.message.text
    kb = ReplyKeyboardMarkup([[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("📞 Telefon raqamingizni yuboring:", reply_markup=kb)
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    phone = update.message.contact.phone_number if update.message.contact else update.message.text
    users[uid]["phone"] = phone
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("💵 Naqd", callback_data="pay_cash")],[InlineKeyboardButton("💳 Click", callback_data="pay_click")]])
    await update.message.reply_text("💰 To'lov usulini tanlang:", reply_markup=kb)
    return PAYMENT

async def pay_cash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    u = users[uid]
    r = RESTAURANTS[u["cafe"]]
    text, total = build_order_text(u, r, q.from_user.first_name)
    text += "💵 To'lov: Naqd (kuryerga beriladi)"
    kb_admin = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Qabul qilish", callback_data=f"accept_{uid}")],[InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{uid}")]])
    try: await context.bot.send_message(chat_id=r["admin_id"], text=text, parse_mode="Markdown", reply_markup=kb_admin)
    except Exception as e: print(e)
    await q.edit_message_text("✅ Buyurtmangiz qabul qilindi! Kafe tasdiqlashi kutilmoqda...")
    users[uid]["cart"] = {}
    return ConversationHandler.END

async def pay_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    u = users[uid]
    r = RESTAURANTS[u["cafe"]]
    _, total = build_order_text(u, r, q.from_user.first_name)
    users[uid]["total"] = total
    await q.edit_message_text(
        f"💳 *Click orqali to'lov - {r['name']}*\n\n"
        f"💰 To'lov miqdori: *{total} so'm*\n\n"
        f"Karta: `{r['click_card']}`\n"
        f"Egasi: {r['click_name']}\n\n"
        f"1. Click ilovasida shu kartaga pul o'tkazing\n"
        f"2. Chekni skrinshot qilib shu yerga rasm qilib yuboring 👇",
        parse_mode="Markdown")
    return CLICK_SCREENSHOT

async def get_click_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = users[uid]
    r = RESTAURANTS[u["cafe"]]
    text, total = build_order_text(u, r, update.effective_user.first_name)
    text += f"💳 To'lov: Click\n💰 To'langan: {total} so'm\n🏦 Qabul qiluvchi karta: {r['click_card']} ({r['click_name']})\n🧾 Chek quyida 👇"
    kb_admin = InlineKeyboardMarkup([[InlineKeyboardButton("✅ To'lovni tasdiqlash", callback_data=f"accept_{uid}")],[InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{uid}")]])
    try:
        photo_id = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=r["admin_id"], photo=photo_id, caption=text, parse_mode="Markdown", reply_markup=kb_admin)
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=r["admin_id"], text=text + "\n(Rasm yuborilmadi)", parse_mode="Markdown", reply_markup=kb_admin)
    await update.message.reply_text("🧾 Chek yuborildi! Admin to'lovni tekshirib tasdiqlaydi...", reply_markup=ReplyKeyboardMarkup([["/start"]], resize_keyboard=True))
    users[uid]["cart"] = {}
    return ConversationHandler.END

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    action, uid_str = q.data.split("_")
    uid = int(uid_str)
    if action == "accept":
        await context.bot.send_message(chat_id=uid, text="✅ Buyurtmangiz va to'lovingiz tasdiqlandi! Tez orada kuryer yo'lga chiqadi.")
        try: await q.edit_message_caption(caption=q.message.caption + "\n\n✅ TASDIQLANDI", parse_mode="Markdown")
        except: await q.edit_message_text(q.message.text + "\n\n✅ QABUL QILINDI", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=uid, text="❌ Afsus, buyurtmangiz rad etildi.")
        try: await q.edit_message_caption(caption=q.message.caption + "\n\n❌ RAD ETILDI", parse_mode="Markdown")
        except: await q.edit_message_text(q.message.text + "\n\n❌ RAD ETILDI", parse_mode="Markdown")

def main():
    Thread(target=lambda: app_flask.run(host="0.0.0.0", port=10000)).start()
    application = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [CallbackQueryHandler(choose_cafe, pattern="^cafe_"), CallbackQueryHandler(add_item, pattern="^add_"), CallbackQueryHandler(show_cart, pattern="^show_cart"), CallbackQueryHandler(clear_cart, pattern="^clear"), CallbackQueryHandler(checkout, pattern="^checkout")],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT & ~filters.COMMAND, get_phone)],
            PAYMENT: [CallbackQueryHandler(pay_cash, pattern="^pay_cash"), CallbackQueryHandler(pay_click, pattern="^pay_click")],
            CLICK_SCREENSHOT: [MessageHandler(filters.PHOTO, get_click_screenshot)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    application.add_handler(conv)
    application.add_handler(CallbackQueryHandler(admin_action, pattern="^(accept|reject)_"))
    application.run_polling()

if __name__ == "__main__":
    main()
