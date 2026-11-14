import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = "9076151422:AAE0VLRsn8EU3gps9c57gc_NoL7VhLHA8C8"
ADMIN_ID = 6738827993
COURIER_GROUP_ID = "@yetqaziberish"
logging.basicConfig(level=logging.INFO)

MENU = {
    "osh": {"name": "Osh - 35000", "price": 35000},
    "shashlik": {"name": "Shashlik - 30000", "price": 30000},
    "lagman": {"name": "Lagman - 28000", "price": 28000},
    "burger": {"name": "Burger - 25000", "price": 25000},
    "pizza": {"name": "Pizza - 55000", "price": 55000},
    "cola": {"name": "Cola - 12000", "price": 12000},
}

user_carts = {}
orders = {}
order_counter = [1]

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Menu", callback_data="menu")],
        [InlineKeyboardButton("Savat", callback_data="cart")],
    ])

def menu_kb():
    btns = []
    for k, v in MENU.items():
        btns.append([InlineKeyboardButton(v["name"], callback_data="add_" + k)])
    btns.append([InlineKeyboardButton("Savat", callback_data="cart")])
    btns.append([InlineKeyboardButton("Bosh menu", callback_data="home")])
    return InlineKeyboardMarkup(btns)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_carts.setdefault(uid, [])
    await update.message.reply_text("Assalomu alaykum! Yetqazib Berish botiga xush kelibsiz!", reply_markup=main_menu())

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = q.from_user.id
    user_carts.setdefault(uid, [])
    if data == "menu":
        await q.edit_message_text("Menudan tanlang:", reply_markup=menu_kb())
    elif data == "home":
        await q.edit_message_text("Bosh menu:", reply_markup=main_menu())
    elif data.startswith("add_"):
        key = data[4:]
        user_carts[uid].append(key)
        await q.answer("Savatga qoshildi!")
    elif data == "cart":
        cart = user_carts[uid]
        if not cart:
            await q.edit_message_text("Savat bosh!", reply_markup=menu_kb())
            return
        total = sum(MENU[k]["price"] for k in cart)
        txt = "Savat:\n"
        for k in cart:
            txt += "- " + MENU[k]["name"] + "\n"
        txt += "\nJami: " + str(total) + " som\nManzilni yozing:"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Tozalash", callback_data="clear")]]))
        context.user_data["wait"] = True
        context.user_data["total"] = total
    elif data == "clear":
        user_carts[uid] = []
        await q.edit_message_text("Savat tozalandi", reply_markup=main_menu())
    elif data.startswith("take_"):
        oid = int(data[5:])
        o = orders.get(oid)
        if not o or o["status"] != "new":
            await q.answer("Bu zakaz olingan!")
            return
        o["status"] = "taken"
        o["courier"] = q.from_user.first_name
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Yetkazdim", callback_data="done_" + str(oid))]])
        try:
            await q.edit_message_text(o["text"] + "\n\nKuryer oldi: " + o["courier"], reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        await q.answer("Zakaz sizga biriktirildi!")
        try:
            await context.bot.send_message(o["user_id"], "Kuryer yolda! " + o["courier"])
        except Exception:
            pass
    elif data.startswith("done_"):
        oid = int(data[5:])
        o = orders.get(oid)
        if not o:
            return
        o["status"] = "done"
        await q.edit_message_text(o["text"] + "\n\nYETKAZILDI!", parse_mode="HTML")
        try:
            await context.bot.send_message(o["user_id"], "Zakazingiz yetkazildi!")
            await context.bot.send_message(ADMIN_ID, "Zakaz #" + str(oid) + " yetkazildi")
        except Exception:
            pass

async def addr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("wait"):
        return
    uid = update.effective_user.id
    cart = user_carts.get(uid, [])
    total = context.user_data.get("total", 0)
    if not cart:
        return
    oid = order_counter[0]
    order_counter[0] += 1
    items = "\n".join(["- " + MENU[k]["name"] for k in cart])
    txt = "<b>YANGI ZAKAZ #" + str(oid) + "</b>\n\nMijoz: " + update.effective_user.first_name + "\nManzil: " + update.message.text + "\n\n" + items + "\n\nJami: " + str(total) + " som"
    orders[oid] = {"text": txt, "status": "new", "user_id": uid}
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Zakazni olish", callback_data="take_" + str(oid))]])
    try:
        await context.bot.send_message(COURIER_GROUP_ID, txt, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text("Kanalga yuborishda xato: " + str(e))
        return
    user_carts[uid] = []
    context.user_data["wait"] = False
    await update.message.reply_text("Zakaz qabul qilindi! #" + str(oid), reply_markup=main_menu())

def main():
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, addr))
    print("Bot ishga tushdi")
    app.run_polling()

if __name__ == "__main__":
    main()
