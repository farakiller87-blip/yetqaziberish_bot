import os, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
COURIER_CHAT_ID = -1003505074098

RESTAURANTS = {
    "asl": {"name": "Asl Burger Yashil Bozor", "admin": 6738827993, "menu": {"Tandir Lavash": 38000, "Lavash Tovuq": 35000}},
    "daxa": {"name": "Daxa", "admin": 6738827993, "menu": {"Osh": 35000, "Cola": 12000}},
}

orders = {}
couriers = set()
order_counter = [1]
main_app = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(r["name"], callback_data=f"cafe_{key}")] for key, r in RESTAURANTS.items()]
    await update.message.reply_text("Qaysi kafedan buyurtma berasiz?\n\nKuryer bo'lsang /kuryer deb yoz.", reply_markup=InlineKeyboardMarkup(kb))

async def cafe_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key = q.data.split("_")[1]
    context.user_data["cafe"] = key
    r = RESTAURANTS[key]
    kb = [[InlineKeyboardButton(f"{name} - {price}", callback_data=f"add_{name}_{price}")] for name, price in r["menu"].items()]
    kb.append([InlineKeyboardButton("✅ Buyurtmani tasdiqlash", callback_data="confirm")])
    await q.edit_message_text(f"🏪 {r['name']}\nMenyu:", reply_markup=InlineKeyboardMarkup(kb))

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, name, price = q.data.split("_")
    cart = context.user_data.get("cart", [])
    cart.append((name, int(price)))
    context.user_data["cart"] = cart
    await q.answer(f"{name} qo'shildi ✅")

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    cafe_key = context.user_data.get("cafe")
    cart = context.user_data.get("cart", [])
    if not cart:
        await q.answer("Savat bo'sh!"); return
    total = sum(p for _, p in cart) + 15000
    oid = order_counter[0]; order_counter[0] += 1
    orders[oid] = {"cafe": cafe_key, "cart": cart, "total": total, "user_id": q.from_user.id, "name": q.from_user.first_name, "status": "waiting"}
    r = RESTAURANTS[cafe_key]
    text = f"🔥 YANGI BUYURTMA #{oid}!\n\n🏪 {r['name']}\n👤 {q.from_user.first_name}\n"
    for n, p in cart: text += f"🛒 {n} - {p}\n"
    text += f"\n🚗 Yetkazib berish: 15000\n💰 JAMI: {total} so'm\n💵 Naqd"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ QABUL QILINDI", callback_data=f"accept_{oid}"), InlineKeyboardButton("❌ RAD ETISH", callback_data=f"reject_{oid}")]])
    await context.bot.send_message(chat_id=r["admin"], text=text, reply_markup=kb)
    await q.edit_message_text("✅ Buyurtmangiz qabul qilindi! Kafe tasdiqlashi kutilmoqda...")

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    action, oid = q.data.split("_"); oid = int(oid)
    order = orders.get(oid)
    if not order: return
    if action == "reject":
        order["status"] = "rejected"
        await context.bot.send_message(chat_id=order["user_id"], text="❌ Buyurtmangiz rad etildi.")
        await q.edit_message_text("❌ Rad etildi"); return
    order["status"] = "to_courier"
    r = RESTAURANTS[order["cafe"]]
    await q.edit_message_text(f"✅ Buyurtma #{oid} qabul qilindi. Kuryerlarga yuborildi.")
    await context.bot.send_message(chat_id=order["user_id"], text="✅ Buyurtmangiz tasdiqlandi! Kuryer qidirilmoqda...")
    ctext = f"🚨 YANGI BUYURTMA #{oid}!\n\n🏪 {r['name']}\n👤 Mijoz: {order['name']}\n💰 {order['total']} so'm\n\nKim birinchi olsa - oshaniki!"
    ckb = InlineKeyboardMarkup([[InlineKeyboardButton("🏃 MEN OLAMAN", callback_data=f"take_{oid}")]])
    try:
        await context.bot.send_message(chat_id=COURIER_CHAT_ID, text=ctext, reply_markup=ckb)
    except Exception as e:
        print(f"Kanalga yuborishda xato: {e}")
    for cid in list(couriers):
        try: await context.bot.send_message(chat_id=cid, text=ctext, reply_markup=ckb)
        except: pass

async def courier_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    couriers.add(update.effective_user.id)
    await update.message.reply_text("🚴 Salom Kuryer!\n\nRo'yxatga olinding ✅\nYangi buyurtma tushishi bilan shu yerga keladi. Kutib tur.")

async def courier_take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    oid = int(q.data.split("_")[1])
    order = orders.get(oid)
    if not order or order["status"] != "to_courier":
        await q.answer("Bu buyurtma allaqachon olingan!"); return
    order["status"] = "taken"; order["courier_id"] = q.from_user.id
    await q.edit_message_text(f"✅ Buyurtma #{oid} seniki!\n\nYetkazib bo'lgach pastni bos:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ YETKAZDIM", callback_data=f"done_{oid}")]]))
    await context.bot.send_message(chat_id=order["user_id"], text=f"🚴 Kuryer yo'lga chiqdi! Buyurtmangiz #{oid} yo'lda.")

async def courier_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    oid = int(q.data.split("_")[1])
    order = orders.get(oid)
    if not order: return
    order["status"] = "done"
    await q.edit_message_text(f"✅ Buyurtma #{oid} yetkazildi. Rahmat!")
    await context.bot.send_message(chat_id=order["user_id"], text=f"✅ Buyurtmangiz #{oid} yetkazildi! Yoqimli ishtaha 😋")

async def main():
    global main_app
    app = Application.builder().token(BOT_TOKEN).build()
    main_app = app
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kuryer", courier_start))
    app.add_handler(CallbackQueryHandler(cafe_menu, pattern="^cafe_"))
    app.add_handler(CallbackQueryHandler(add_item, pattern="^add_"))
    app.add_handler(CallbackQueryHandler(confirm, pattern="^confirm$"))
    app.add_handler(CallbackQueryHandler(admin_action, pattern="^(accept|reject)_"))
    app.add_handler(CallbackQueryHandler(courier_take, pattern="^take_"))
    app.add_handler(CallbackQueryHandler(courier_done, pattern="^done_"))
    print("Bot ishga tushdi...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
