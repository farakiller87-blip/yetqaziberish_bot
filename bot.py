import os, json, asyncio
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)
Thread(target=run_flask, daemon=True).start()
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SUPER_ADMIN = 6738827993
COURIER_CHANNEL = -1003505074098
DB_FILE = "db.json"

# --- BAZA ---
def load():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users": {}, "restaurants": {
        "asl": {"name": "Asl Burger Yashil Bozor", "admin": 6738827993, "menu": {"Tandir Lavash": 38000, "Lavash Tovuq": 35000}, "active": True},
        "asl 5 kichik daxa": {"name": "Asl Burger 5 kichik Daxa", "admin": 6738827993, "menu": {"Osh": 35000, "Cola": 12000}, "active": True}
    }, "orders": {}, "counter": 1}

def save():
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(DB, f, ensure_ascii=False, indent=2)

DB = load()

# --- YORDAMCHI ---
def main_kb(role):
    if role == "courier":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 ONLINE / 🔴 OFFLINE", callback_data="courier_toggle")],
            [InlineKeyboardButton("📦 Bo'sh buyurtmalar", callback_data="courier_list")],
            [InlineKeyboardButton("🚴 Mening buyurtmam", callback_data="courier_my")],
            [InlineKeyboardButton("💰 Mening hisobim", callback_data="courier_balance")],
            [InlineKeyboardButton("🔄 Rolni o'zgartirish", callback_data="change_role")]
        ])
    if role == "restaurant":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Yangi buyurtmalar", callback_data="rest_orders")],
            [InlineKeyboardButton("🍔 Menyuni ko'rish", callback_data="rest_menu")],
            [InlineKeyboardButton("📊 Bugungi statistika", callback_data="rest_stats")],
            [InlineKeyboardButton("🔄 Rolni o'zgartirish", callback_data="change_role")]
        ])
    if role == "admin":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Barcha buyurtmalar", callback_data="admin_orders")],
            [InlineKeyboardButton("🏪 Restoranlar", callback_data="admin_rests")],
            [InlineKeyboardButton("🚴 Kuryerlar", callback_data="admin_couriers")],
            [InlineKeyboardButton("👥 Mijozlar", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton("🔄 Rolni o'zgartirish", callback_data="change_role")]
        ])
    # mijoz
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍔 Buyurtma berish", callback_data="client_order")],
        [InlineKeyboardButton("📦 Mening buyurtmalarim", callback_data="client_my")],
        [InlineKeyboardButton("🔄 Rolni o'zgartirish", callback_data="change_role")]
    ])

async def show_main(update, user_id, text="Asosiy menyu:"):
    u = DB["users"].get(str(user_id), {})
    role = u.get("role", "client")
    kb = main_kb(role)
    if update.callback_query:
        try: await update.callback_query.edit_message_text(text, reply_markup=kb)
        except: await update.callback_query.message.reply_text(text, reply_markup=kb)
    else:
        await update.message.reply_text(text, reply_markup=kb)

# --- START / ROL TANLASH ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in DB["users"]:
        DB["users"][uid] = {"name": update.effective_user.first_name, "role": "client", "phone": "", "online": False, "balance": 0, "delivered": 0}
        save()
    u = DB["users"][uid]
    # Super admin har doim admin menyusini ko'radi
    if update.effective_user.id == SUPER_ADMIN:
        await update.message.reply_text(f"👑 Salom Boss!\n\nSen Super Adminsan. Qaysi rolni ko'rmoqchisan?", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Admin panel", callback_data="setrole_admin")],
            [InlineKeyboardButton("🍔 Mijoz sifatida", callback_data="setrole_client")],
            [InlineKeyboardButton("🚴 Kuryer sifatida", callback_data="setrole_courier")],
            [InlineKeyboardButton("🏪 Restoran sifatida", callback_data="setrole_restaurant")],
        ]))
        return
    await show_main(update, update.effective_user.id, f"Salom {u['name']}! 👋\n\nHozirgi roling: {u['role']}\nTanla:")

async def set_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    role = q.data.replace("setrole_", "")
    uid = str(q.from_user.id)
    DB["users"][uid]["role"] = role; save()
    await show_main(update, q.from_user.id, f"Rol o'zgardi: {role} ✅")

async def change_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = q.from_user.id
    if uid == SUPER_ADMIN:
        await q.edit_message_text("Qaysi rol?", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Admin", callback_data="setrole_admin")],
            [InlineKeyboardButton("🍔 Mijoz", callback_data="setrole_client")],
            [InlineKeyboardButton("🚴 Kuryer", callback_data="setrole_courier")],
            [InlineKeyboardButton("🏪 Restoran", callback_data="setrole_restaurant")],
        ])); return
    await q.edit_message_text("Rolingni tanla:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🍔 Mijoz", callback_data="setrole_client")],
        [InlineKeyboardButton("🚴 Kuryer", callback_data="setrole_courier")],
        [InlineKeyboardButton("🏪 Restoran egasi", callback_data="setrole_restaurant")],
    ]))

# --- MIJOZ ---
async def client_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    kb = [[InlineKeyboardButton(r["name"], callback_data=f"cafe_{key}")] for key, r in DB["restaurants"].items() if r.get("active")]
    kb.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")])
    await q.edit_message_text("Qaysi restorandan buyurtma berasiz?", reply_markup=InlineKeyboardMarkup(kb))

async def cafe_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key = q.data.split("_")[1]
    context.user_data["cafe"] = key
    context.user_data["cart"] = []
    r = DB["restaurants"][key]
    kb = [[InlineKeyboardButton(f"{n} - {p} so'm", callback_data=f"add_{n}_{p}")] for n, p in r["menu"].items()]
    kb.append([InlineKeyboardButton("✅ Savatni tasdiqlash", callback_data="confirm_cart")])
    kb.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="client_order")])
    await q.edit_message_text(f"🏪 {r['name']}\nMenyu:", reply_markup=InlineKeyboardMarkup(kb))

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, name, price = q.data.split("_")
    cart = context.user_data.get("cart", []); cart.append((name, int(price)))
    context.user_data["cart"] = cart
    await q.answer(f"{name} qo'shildi ✅ | Savat: {len(cart)} ta")

async def confirm_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    cart = context.user_data.get("cart", [])
    if not cart: await q.answer("Savat bo'sh!"); return
    context.user_data["step"] = "phone"
    await q.edit_message_text("📞 Telefon raqamingizni yuboring:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📞 Raqamni yuborish", callback_data="send_phone_btn")]]))
    # Telefonni contact orqali olish uchun Reply tugma
    await q.message.reply_text("Pastdagi tugmani bosib raqamingizni yuboring 👇", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
async def pay_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == "pay_naqd":
        context.user_data["payment"] = "Naqd 💵"
    else:
        context.user_data["payment"] = "Click 💳"
    context.user_data["step"] = "address"
    await q.message.reply_text("📍 Manzilingizni yozing (Masalan: Yashil Bozor, 5-uy):", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]], resize_keyboard=True, one_time_keyboard=True))
async def on_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.contact: return
    uid = str(update.effective_user.id)
    DB["users"][uid]["phone"] = update.message.contact.phone_number; save()
    if context.user_data.get("step") == "phone":
    context.user_data["step"] = "payment"
    await update.message.reply_text("💳 To'lov turini tanlang:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💵 Naqd", callback_data="pay_naqd"), InlineKeyboardButton("💳 Click", callback_data="pay_click")]]))
    return
    elif context.user_data.get("step") == "courier_phone":
        await update.message.reply_text("✅ Kuryer sifatida ro'yxatdan o'tding! Endi ONLINE bo'l.")
        await show_main(update, update.effective_user.id)

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") != "address":
         await show_main(update, update.effective_user.id, "🏠 Asosiy menyu:")
        return
    address = update.message.text
    cart = context.user_data.get("cart", []); cafe_key = context.user_data.get("cafe")
    total = sum(p for _, p in cart) + 15000
    oid = DB["counter"]; DB["counter"] += 1
    uid = str(update.effective_user.id)
    payment = context.user_data.get("payment", "Naqd 💵")
    DB["orders"][str(oid)] = {"id": oid, "cafe": cafe_key, "cart": cart, "total": total, "payment": payment, "user_id": int(uid), "name": DB["users"][uid]["name"], "phone": DB["users"][uid].get("phone",""), "address": address, "status": "waiting", "courier_id": None, "created": "now"}
    save()
    context.user_data["step"] = None
    r = DB["restaurants"][cafe_key]
    text = f"🔥 YANGI BUYURTMA #{oid}!\n\n🏪 {r['name']}\n👤 {DB['users'][uid]['name']} | 📞 {DB['users'][uid].get('phone')}\n📍 {address}\n"
    for n, p in cart: text += f"🛒 {n} - {p}\n"
    text += f"\n🚗 Yetkazib berish: 15000\n💰 JAMI: {total} so'm | {payment}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ QABUL QILISH", callback_data=f"accept_{oid}"), InlineKeyboardButton("❌ RAD ETISH", callback_data=f"reject_{oid}")]])
    await context.bot.send_message(chat_id=r["admin"], text=text, reply_markup=kb)
    await context.bot.send_message(chat_id=SUPER_ADMIN, text=text)
    await update.message.reply_text("✅ Buyurtmangiz yuborildi! Restoran tasdiqlashi kutilmoqda...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Asosiy", callback_data="back_main")]]))

# --- RESTORAN ---
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    action, oid = q.data.split("_"); oid = str(oid)
    order = DB["orders"].get(oid)
    if not order: await q.answer("Topilmadi"); return
    if action == "reject":
        order["status"] = "rejected"; save()
        await context.bot.send_message(chat_id=order["user_id"], text=f"❌ Buyurtma #{oid} rad etildi.")
        await q.edit_message_text("❌ Rad etildi"); return
    order["status"] = "to_courier"; save()
    r = DB["restaurants"][order["cafe"]]
    await q.edit_message_text(f"✅ Buyurtma #{oid} qabul qilindi. Kuryerlarga yuborildi.")
    await context.bot.send_message(chat_id=order["user_id"], text="✅ Buyurtmangiz tasdiqlandi! Kuryer qidirilmoqda...")
    # Kanalga + online kuryerlarga
    ctext = f"🚨 YANGI BUYURTMA #{oid}!\n\n🏪 {r['name']}\n📍 {order['address']}\n👤 {order['name']} | 📞 {order['phone']}\n💰 {order['total']} so'm\n\nKim birinchi olsa - oshaniki!"
    ckb = InlineKeyboardMarkup([[InlineKeyboardButton("🏃 MEN OLAMAN", callback_data=f"take_{oid}")]])
    try: await context.bot.send_message(chat_id=COURIER_CHANNEL, text=ctext, reply_markup=ckb)
    except Exception as e: print("Kanal xato:", e)
    for uid, u in DB["users"].items():
        if u.get("role") == "courier" and u.get("online"):
            try: await context.bot.send_message(chat_id=int(uid), text=ctext, reply_markup=ckb)
            except: pass

# --- KURYER ---
async def courier_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = str(q.from_user.id)
    u = DB["users"][uid]
    if not u.get("phone"):
        context.user_data["step"] = "courier_phone"
        await q.message.reply_text("Avval telefon raqamingizni yuboring:", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
        return
    u["online"] = not u.get("online"); save()
    await q.answer("ONLINE ✅" if u["online"] else "OFFLINE 🔴")
    await show_main(update, q.from_user.id, f"Holat: {'🟢 ONLINE' if u['online'] else '🔴 OFFLINE'}")

async def courier_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    orders = [o for o in DB["orders"].values() if o["status"] == "to_courier"]
    if not orders: await q.edit_message_text("Hozircha bo'sh buyurtma yo'q.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]])); return
    kb = []
    for o in orders:
        kb.append([InlineKeyboardButton(f"#{o['id']} | {DB['restaurants'][o['cafe']]['name']} | {o['total']} so'm | {o['address'][:30]}", callback_data=f"take_{o['id']}")])
    kb.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")])
    await q.edit_message_text("📦 Bo'sh buyurtmalar:", reply_markup=InlineKeyboardMarkup(kb))

async def courier_take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    oid = str(q.data.split("_")[1])
    order = DB["orders"].get(oid)
    if not order or order["status"] != "to_courier":
        await q.answer("Bu buyurtma allaqachon olingan!"); return
    order["status"] = "taken"; order["courier_id"] = q.from_user.id; save()
    u = DB["users"][str(q.from_user.id)]
    await q.edit_message_text(f"✅ Buyurtma #{oid} seniki!\n\n📍 Manzil: {order['address']}\n📞 Mijoz: {order['phone']}\n💰 {order['total']} so'm\n\nYetkazib bo'lgach pastni bos:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ YETKAZDIM", callback_data=f"done_{oid}")]]))
    await context.bot.send_message(chat_id=order["user_id"], text=f"🚴 Kuryer {u['name']} yo'lga chiqdi! Buyurtma #{oid} yo'lda.")
    # Restoranga ham xabar
    await context.bot.send_message(chat_id=DB["restaurants"][order["cafe"]]["admin"], text=f"🚴 Kuryer {u['name']} buyurtma #{oid} ni oldi.")

async def courier_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    oid = str(q.data.split("_")[1]); order = DB["orders"].get(oid)
    if not order: return
    order["status"] = "done"; save()
    uid = str(q.from_user.id); DB["users"][uid]["delivered"] = DB["users"][uid].get("delivered", 0) + 1; DB["users"][uid]["balance"] = DB["users"][uid].get("balance", 0) + 15000; save()
    await q.edit_message_text(f"✅ Buyurtma #{oid} yetkazildi! +15000 so'm hisobingga qo'shildi.")
    await context.bot.send_message(chat_id=order["user_id"], text=f"✅ Buyurtmangiz #{oid} yetkazildi! Yoqimli ishtaha 😋\n\nKuryerni baholang:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⭐️⭐️⭐️⭐️⭐️", callback_data=f"rate_5_{oid}"), InlineKeyboardButton("⭐️⭐️⭐️", callback_data=f"rate_3_{oid}")]]))
    await context.bot.send_message(chat_id=SUPER_ADMIN, text=f"✅ #{oid} yetkazildi. Kuryer: {DB['users'][uid]['name']}")

# --- ADMIN PANEL ---
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    total = len(DB["orders"]); done = len([o for o in DB["orders"].values() if o["status"] == "done"])
    couriers = len([u for u in DB["users"].values() if u.get("role") == "courier"])
    online = len([u for u in DB["users"].values() if u.get("role") == "courier" and u.get("online")])
    clients = len([u for u in DB["users"].values() if u.get("role") == "client"])
    await q.edit_message_text(f"📊 STATISTIKA\n\n📦 Jami buyurtma: {total}\n✅ Yetkazilgan: {done}\n🚴 Kuryerlar: {couriers} ta (online: {online})\n👥 Mijozlar: {clients} ta\n🏪 Restoranlar: {len(DB['restaurants'])} ta", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))

async def generic_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == "back_main": await show_main(update, q.from_user.id)
    elif q.data == "client_order": await client_order(update, context)
    elif q.data == "courier_my":
        oid_list = [o for o in DB["orders"].values() if o.get("courier_id") == q.from_user.id and o["status"] == "taken"]
        if not oid_list: await q.edit_message_text("Hozircha olingan buyurtmang yo'q.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]])); return
        o = oid_list[0]; await q.edit_message_text(f"🚴 Buyurtma #{o['id']}\n📍 {o['address']}\n📞 {o['phone']}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ YETKAZDIM", callback_data=f"done_{o['id']}")]]))
    elif q.data == "courier_balance":
        u = DB["users"][str(q.from_user.id)]; await q.edit_message_text(f"💰 Balans: {u.get('balance',0)} so'm\n✅ Yetkazgan: {u.get('delivered',0)} ta", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
    elif q.data == "client_my":
        my = [o for o in DB["orders"].values() if o["user_id"] == q.from_user.id]
        if not my: await q.edit_message_text("Hali buyurtma bermagansan.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]])); return
        txt = "📦 Buyurtmalaring:\n\n" + "\n".join([f"#{o['id']} | {o['status']} | {o['total']} so'm" for o in my[-5:]])
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
    elif q.data in ["admin_orders","rest_orders"]:
        txt = "📦 Oxirgi buyurtmalar:\n\n" + "\n".join([f"#{o['id']} | {o['status']} | {o['total']} so'm | {o['address'][:20]}" for o in list(DB["orders"].values())[-10:]]) if DB["orders"] else "Yo'q"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
    elif q.data == "admin_couriers":
        txt = "🚴 Kuryerlar:\n\n" + "\n".join([f"{u['name']} | {'🟢' if u.get('online') else '🔴'} | {u.get('delivered',0)} ta | {u.get('balance',0)} so'm" for u in DB["users"].values() if u.get("role")=="courier"]) or "Yo'q"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
    elif q.data == "admin_users":
        await q.edit_message_text(f"👥 Jami foydalanuvchi: {len(DB['users'])}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
    elif q.data == "admin_rests":
        txt = "🏪 Restoranlar:\n\n" + "\n".join([f"{r['name']} | {len(r['menu'])} ta taom" for r in DB["restaurants"].values()])
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
    elif q.data in ["rest_menu","rest_stats"]:
        await q.edit_message_text("Bu bo'lim tez orada... Hozircha Admin paneldan ko'r.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))

import asyncio
async def on_location(update, context):
    if not update.message.location:
        return
    loc = update.message.location
    update.message.text = f"📍 Lokatsiya: https://maps.google.com/?q={loc.latitude},{loc.longitude}"
    await on_text(update, context)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_role, pattern="^setrole_"))
    app.add_handler(CallbackQueryHandler(change_role, pattern="^change_role$"))
    app.add_handler(CallbackQueryHandler(client_order, pattern="^client_order$"))
    app.add_handler(CallbackQueryHandler(cafe_menu, pattern="^cafe_"))
    app.add_handler(CallbackQueryHandler(add_item, pattern="^add_"))
    app.add_handler(CallbackQueryHandler(confirm_cart, pattern="^confirm_cart$"))
    app.add_handler(CallbackQueryHandler(admin_action, pattern="^(accept|reject)_"))
    app.add_handler(CallbackQueryHandler(courier_toggle, pattern="^courier_toggle$"))
    app.add_handler(CallbackQueryHandler(courier_list, pattern="^courier_list$"))
    app.add_handler(CallbackQueryHandler(courier_take, pattern="^take_"))
    app.add_handler(CallbackQueryHandler(courier_done, pattern="^done_"))
    app.add_handler(CallbackQueryHandler(courier_done, pattern="^done_"))
    app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(generic_back, pattern="^(back_main|client_my|courier_my|courier_balance|admin_orders|rest_orders|admin_couriers|admin_users|admin_rests|rest_menu|rest_stats)$"))
    app.add_handler(MessageHandler(filters.CONTACT, on_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(filters.LOCATION, on_location))
    print("Yandex-style bot ishga tushdi...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    # Botni to'xtamasdan ushlab turamiz
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    main()
