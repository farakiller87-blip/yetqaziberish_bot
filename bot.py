import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- СОЗЛАМАЛАР ---
TOKEN = "9076151422:AAE0VLRsn8EU3gps9c57gc_NoL7VhLHA8C8"
ADMIN_ID = 6738827993
COURIER_GROUP_ID = "@yetqaziberish"  # Сенинг каналинг

logging.basicConfig(level=logging.INFO)

# --- МЕНЮ ---
MENU = {
    "osh": {"name": "🍚 Ош - 35 000 сўм", "price": 35000},
    "shashlik": {"name": "🍢 Шашлик - 30 000 сўм", "price": 30000},
    "lagman": {"name": "🍜 Лағмон - 28 000 сўм", "price": 28000},
    "burger": {"name": "🍔 Бургер - 25 000 сўм", "price": 25000},
    "pizza": {"name": "🍕 Пицца - 55 000 сўм", "price": 55000},
    "cola": {"name": "🥤 Кола - 12 000 сўм", "price": 12000},
}

user_carts = {}
orders = {}
order_counter = 1

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍽️ Менюни кўриш", callback_data="menu")],
        [InlineKeyboardButton("🛒 Сават (0)", callback_data="cart")],
        [InlineKeyboardButton("📞 Админ билан боғланиш", callback_data="contact")],
    ])

def menu_keyboard():
    buttons = []
    for key, item in MENU.items():
        buttons.append([InlineKeyboardButton(item["name"], callback_data=f"add_{key}")])
    buttons.append([InlineKeyboardButton("🛒 Саватни кўриш", callback_data="cart")])
    buttons.append([InlineKeyboardButton("🏠 Бош меню", callback_data="home")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_carts:
        user_carts[user_id] = []
    await update.message.reply_text(
        "Ассалому алайкум! 👋\n\n"
        "🍽️ <b>Yetqazib Berish</b> ботига хуш келибсиз!\n"
        "Термиз бўйича тезкор етказиб бериш хизмати.\n\n"
        "Менюдан танланг:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_name = query.from_user.first_name

    if user_id not in user_carts:
        user_carts[user_id] = []

    # --- МЕНЮ ---
    if data == "menu":
        await query.edit_message_text("🍽️ Менюдан танланг:", reply_markup=menu_keyboard())
    elif data == "home":
        await query.edit_message_text("Бош меню:", reply_markup=main_menu())
    elif data.startswith("add_"):
        key = data.replace("add_", "")
        user_carts[user_id].append(key)
        item = MENU[key]
        await query.answer(f"✅ {item['name']} саватга қўшилди!")
        # Сават тугмасини янгилаш
        await query.edit_message_text("🍽️ Менюдан танланг:", reply_markup=menu_keyboard())

    # --- САВАТ ---
    elif data == "cart":
        cart = user_carts[user_id]
        if not cart:
            await query.edit_message_text("🛒 Сават бўш!\nМенюдан бирор нарса танланг.", reply_markup=menu_keyboard())
            return
        text = "🛒 <b>Саватингиз:</b>\n\n"
        total = 0
        for key in cart:
            text += f"• {MENU[key]['name']}\n"
            total += MENU[key]['price']
        text += f"\n💰 <b>Жами: {total:,} сўм</b>\n\nМанзилингизни ёзинг (масалан: А.Навоий 12, 3-подъезд):"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Саватни тозалаш", callback_data="clear")],
            [InlineKeyboardButton("🏠 Бош меню", callback_data="home")]
        ])
        await query.edit_message_text(text, reply_markup=kb, parse_mode="HTML")
        context.user_data["waiting_address"] = True
        context.user_data["total"] = total

    elif data == "clear":
        user_carts[user_id] = []
        await query.edit_message_text("🛒 Сават тозаланди.", reply_markup=main_menu())

    elif data == "contact":
        await query.edit_message_text("📞 Админ: @yetqaziberish\nТелефон: +998 90 000-00-00", reply_markup=main_menu())
# --- КУРЬЕР ОЛДИ ---
    elif data.startswith("take_"):
        order_id = data.replace("take_", "")
        order = orders.get(int(order_id))
        if not order:
            await query.answer("Бу заказ топилмади!")
            return
        if order["status"] != "new":
            await query.answer("Бу заказни бошқа курьер олган!")
            return
        order["status"] = "taken"
        order["courier"] = user_name
        order["courier_id"] = user_id
        # Каналдаги хабарни янгилаш
        new_text = order["text"] + f"\n\n✅ <b>Курьер олди:</b> {user_name}"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Етказиб бердим", callback_data=f"done_{order_id}")],
            [InlineKeyboardButton("❌ Бекор қилиш", callback_data=f"cancel_{order_id}")]
        ])
        try:
            await query.edit_message_text(new_text, reply_markup=kb, parse_mode="HTML")
        except:
            pass
        await query.answer("✅ Заказ сизга бириктирилди!")
        # Мижозга хабар
        try:
            await context.bot.send_message(order["user_id"], f"🛵 Курьерингиз йўлга чиқди! {user_name} заказни олиб келмоқда.")
        except:
            pass

    elif data.startswith("done_"):
        order_id = data.replace("done_", "")
        order = orders.get(int(order_id))
        if not order:
            return
        order["status"] = "done"
        await query.edit_message_text(order["text"] + f"\n\n🎉 <b>ЕТКАЗИЛДИ!</b> Курьер: {order['courier']}", parse_mode="HTML")
        await query.answer("Раҳмат!")
        try:
            await context.bot.send_message(order["user_id"], "🎉 Заказингиз етказилди! Ёқимли иштаҳа! 😋")
            await context.bot.send_message(ADMIN_ID, f"✅ Заказ #{order_id} етказилди. Курьер: {order['courier']}")
        except:
            pass

    elif data.startswith("cancel_"):
        order_id = data.replace("cancel_", "")
        order = orders.get(int(order_id))
        order["status"] = "new"
        order["courier"] = None
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛵 Заказни олиш", callback_data=f"take_{order_id}")]])
        await query.edit_message_text(order["text"], reply_markup=kb, parse_mode="HTML")
        await query.answer("Заказ бекор қилинди, қайта чиқди.")

async def address_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_counter
    if not context.user_data.get("waiting_address"):
        return
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    address = update.message.text
    cart = user_carts.get(user_id, [])
    total = context.user_data.get("total", 0)

    if not cart:
        await update.message.reply_text("Сават бўш!")
        return

    order_id = order_counter
    order_counter += 1

    items_text = "\n".join([f"• {MENU[k]['name']}" for k in cart])
    text = (
        f"🆕 <b>ЯНГИ ЗАКАЗ #{order_id}</b>\n\n"
        f"👤 Мижоз: {user_name}\n"
        f"📍 Манзил: {address}\n"
        f"📞 ID: {user_id}\n\n"
        f"🍽️ <b>Заказ:</b>\n{items_text}\n\n"
        f"💰 <b>Жами: {total:,} сўм</b>\n"
        f"💳 Тўлов: Нақд / Карта"
    )
    orders[order_id] = {"text": text, "status": "new", "user_id": user_id, "courier": None}

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛵 Заказни олиш", callback_data=f"take_{order_id}")]])

    # Каналга юбориш
    try:
        await context.bot.send_message(COURIER_GROUP_ID, text, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Каналга юборишда хатолик: {e}\nБот каналда админлигини текшир!")
        return

    # Админга ҳам
    try:
        await context.bot.send_message(ADMIN_ID, text, parse_mode="HTML")
    except:
        pass

    user_carts[user_id] = []
    context.user_data["waiting_address"] = False
    await update.message.reply_text(
        f"✅ Заказингиз қабул қилинди! #{order_id}\n\n"
        f"Курьер топилиши билан хабар берамиз. 🛵\n"
        f"Жами: {total:,} сўм",
        reply_markup=main_menu()
    )def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, address_handler))
    print("Бот ишга тушди...")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
