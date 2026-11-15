import os, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
COURIER_TOKEN = os.environ.get("COURIER_BOT_TOKEN")

# --- MA'LUMOTLAR ---
# Bu yerga o'zingning restoranlaringni yoz
RESTAURANTS = {
    "asl": {"name": "Asl Burger Yashil Bozor", "admin": 6738827993, "menu": {"Tandir Lavash": 38000, "Lavash Tovuq": 35000}},
    "daxa": {"name": "Daxa", "admin": 6738827993, "menu": {"Osh": 35000, "Cola": 12000}},
}

orders = {}  # order_id -> order info
couriers = set()  # kuryerlar ID si
order_counter = [1]
main_app = None
courier_app = None

# --- MIJOZ BOTI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(r["name"], callback_data=f"cafe_{key}")] for key, r in RESTAURANTS.items()]
    await update.message.reply_text("Qaysi kafedan buyurtma berasiz?", reply_markup=InlineKeyboardMarkup(kb))

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
    # QABUL QILINDI -> KURYERLARGA YUBORISH
    order["status"] = "to_courier"
    r = RESTAURANTS[order["cafe"]]
    await q.edit_message_text(f"✅ Buyurtma #{oid} qabul qilindi. Kuryerlarga yuborildi.")
    await context.bot.send_message(chat_id=order["user_id"], text="✅ Buyurtmangiz tasdiqlandi! Kuryer qidirilmoqda...")
    # --- BOG'LANISH JOYI: Kuryer boti orqali hamma kuryerga ---
    ctext = f"🚨 YANGI BUYURTMA #{oid}!\n\n🏪 {r['name']}\n👤 Mijoz: {order['name']}\n💰 {order['total']} so'm\n\nKim birinchi olsa - oshaniki!"
    ckb = InlineKeyboardMarkup([[InlineKeyboardButton("🏃 MEN OLAMAN", callback_data=f"take_{oid}")]])
    for cid in list(couriers):
        try: await courier_app.bot.send_message(chat_id=cid, text=ctext, reply_markup=ckb)
        except: pass
    if not couriers:
        await context.bot.send_message(chat_id=r["admin"], text="⚠️ Hozircha ro'yxatdan o'tgan kuryer yo'q! Kuryer @yetqaziberish botiga /start bossin.")

# --- KURYER BOTI ---
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
    await main_app.bot.send_message(chat_id=order["user_id"], text=f"🚴 Kuryer yo'lga chiqdi! Buyurtmangiz #{oid} yo'lda.")

async def courier_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    oid = int(q.data.split("_")[1])
    order = orders.get(oid)
    order["status"] = "done"
    await q.edit_message_text(f"✅ Buyurtma #{oid} yetkazildi. Rahmat!")
    await main_app.bot.send_message(chat_id=order["user_id"], text=f"✅ Buyurtmangiz #{oid} yetkazildi! Yoqimli ishtaha 😋")

async def main():
    global main_app, courier_app
    main_app = Application.builder().token(BOT_TOKEN).build()
    main_app.add_handler(CommandHandler("start", start))
    main_app.add_handler(CallbackQueryHandler(cafe_menu, pattern="^cafe_"))
    main_app.add_handler(CallbackQueryHandler(add_item, pattern="^add_"))
    main_app.add_handler(CallbackQueryHandler(confirm, pattern="^confirm$"))
    main_app.add_handler(CallbackQueryHandler(admin_action, pattern="^(accept|reject)_"))
    courier_app = Application.builder().token(COURIER_TOKEN).build()
    courier_app.add_handler(CommandHandler("start", courier_start))
    courier_app.add_handler(CallbackQueryHandler(courier_take, pattern="^take_"))
    courier_app.add_handler(CallbackQueryHandler(courier_done, pattern="^done_"))
    await asyncio.gather(main_app.initialize(), courier_app.initialize())
    await asyncio.gather(main_app.start(), courier_app.start())
    await asyncio.gather(main_app.updater.start_polling(), courier_app.updater.start_polling())
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
