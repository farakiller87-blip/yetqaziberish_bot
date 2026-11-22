# TERMIZ OVQAT BOTI - SENING BOTING + 9 TA OSHXONA BIRLASHTIRILDI
# Eski botingning hamma funksiyasi saqlandi: kuryer, reyting, admin, restoran.
# Qo'shilgan: 9 ta Termiz oshxonasi, har birida o'z delivery narxi, Payme to'lovi, 100 000 dan yuqoriga bepul yetkazish.
# Ishga tushirish: BOT_TOKEN ni Render Environment da qo'yganingcha qoldir, db.json eski bo'lsa o'chir - yangi restoranlar chiqishi uchun.
# requirements.txt: python-telegram-bot==22.2 + Flask (o'sha faylingni ishlat)

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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
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
        "diplomat": {"name": "Diplomat Restaurant", "admin": 6738827993, "delivery": 15000, "menu": {"Shashlik": 45000, "Osh": 38000, "Lagman": 32000, "Pizza": 65000, "Shorva": 28000}, "active": True},
        "imix": {"name": "I'm Mix", "admin": 6738827993, "delivery": 10000, "menu": {"Burger": 35000, "Lavash": 38000, "Hot-dog": 22000, "Fries": 18000, "Cola": 12000}, "active": True},
        "somsa": {"name": "Somsa City", "admin": 6738827993, "delivery": 10000, "menu": {"Somsa goshtli": 12000, "Somsa tovuqli": 10000, "Somsa kartoshkali": 8000, "Choy": 5000}, "active": True},
        "osiyo": {"name": "Restoran Osiyo", "admin": 6738827993, "delivery": 15000, "menu": {"Osh": 35000, "Manti": 30000, "Shashlik": 42000, "Norin": 33000}, "active": True},
        "sabr": {"name": "Sabr milliy taomlar", "admin": 6738827993, "delivery": 12000, "menu": {"Osh": 32000, "Shashlik": 40000, "Qozon kabob": 48000, "Shorva": 25000}, "active": True},
        "garik": {"name": "GARIK kafesi", "admin": 6738827993, "delivery": 12000, "menu": {"Shashlik": 40000, "Lavash": 30000, "Burger": 28000, "Choy": 5000}, "active": True},
        "coffee": {"name": "Coffee Truck", "admin": 6738827993, "delivery": 10000, "menu": {"Kofe": 18000, "Kapuchino": 22000, "Latte": 24000, "Kruassan": 15000}, "active": True},
        "yapo": {"name": "Yapo Sushi", "admin": 6738827993, "delivery": 15000, "menu": {"Sushi set": 85000, "Roll": 45000, "Ramen": 48000, "Miso shorva": 20000}, "active": True},
        "aqilli": {"name": "Aqilli bekat", "admin": 6738827993, "delivery": 8000, "menu": {"Kofe": 15000, "Choy": 6000, "Sendvich": 20000, "Shirinlik": 18000}, "active": True}
    }, "orders": {}, "counter": 1}

def save():
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(DB, f, ensure_ascii=False, indent=2)

DB = load()
# --- MIGRATSIYA: eski db.json bo'lsa ham yangi 9 ta oshxonani qo'shadi ---
_NEW_RESTS = {
    "diplomat": {"name": "Diplomat Restaurant", "admin": 6738827993, "delivery": 15000, "menu": {"Shashlik": 45000, "Osh": 38000, "Lagman": 32000, "Pizza": 65000, "Shorva": 28000}, "active": True},
    "imix": {"name": "I'm Mix", "admin": 6738827993, "delivery": 10000, "menu": {"Burger": 35000, "Lavash": 38000, "Hot-dog": 22000, "Fries": 18000, "Cola": 12000}, "active": True},
    "somsa": {"name": "Somsa City", "admin": 6738827993, "delivery": 10000, "menu": {"Somsa goshtli": 12000, "Somsa tovuqli": 10000, "Somsa kartoshkali": 8000, "Choy": 5000}, "active": True},
    "osiyo": {"name": "Restoran Osiyo", "admin": 6738827993, "delivery": 15000, "menu": {"Osh": 35000, "Manti": 30000, "Shashlik": 42000, "Norin": 33000}, "active": True},
    "sabr": {"name": "Sabr milliy taomlar", "admin": 6738827993, "delivery": 12000, "menu": {"Osh": 32000, "Shashlik": 40000, "Qozon kabob": 48000, "Shorva": 25000}, "active": True},
    "garik": {"name": "GARIK kafesi", "admin": 6738827993, "delivery": 12000, "menu": {"Shashlik": 40000, "Lavash": 30000, "Burger": 28000, "Choy": 5000}, "active": True},
    "coffee": {"name": "Coffee Truck", "admin": 6738827993, "delivery": 10000, "menu": {"Kofe": 18000, "Kapuchino": 22000, "Latte": 24000, "Kruassan": 15000}, "active": True},
    "yapo": {"name": "Yapo Sushi", "admin": 6738827993, "delivery": 15000, "menu": {"Sushi set": 85000, "Roll": 45000, "Ramen": 48000, "Miso shorva": 20000}, "active": True},
    "aqilli": {"name": "Aqilli bekat", "admin": 6738827993, "delivery": 8000, "menu": {"Kofe": 15000, "Choy": 6000, "Sendvich": 20000, "Shirinlik": 18000}, "active": True},
}
_changed = False
for _k, _v in _NEW_RESTS.items():
    if _k not in DB.get("restaurants", {}):
        DB["restaurants"][_k] = _v; _changed = True
# Eski 2 ta Asl Burger ni o'chirmadik - xohlasang Render da db.json dan o'chirish mumkin, hozir 9+2 = 11 ta bo'ladi
if _changed: save()


# --- YORDAMCHI ---
def main_kb(role):
    if role == "courier":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🚴 Mening kuryer panelim", callback_data="courier_panel")],
            [InlineKeyboardButton("🟢 ONLINE / 🔴 OFFLINE", callback_data="courier_toggle")],
            [InlineKeyboardButton("📦 Bo'sh buyurtmalar", callback_data="courier_list")],
            [InlineKeyboardButton("🚴 Mening buyurtmam", callback_data="courier_my")],
            [InlineKeyboardButton("💰 Mening hisobim", callback_data="courier_balance_new")],
        ])
    if role == "restaurant":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏪 Mening restoran panelim", callback_data="rest_panel")],
            [InlineKeyboardButton("📦 Yangi buyurtmalar", callback_data="rest_orders")],
            [InlineKeyboardButton("🍔 Menyuni boshqarish", callback_data="rest_menu")],
            [InlineKeyboardButton("📊 Bugungi statistika", callback_data="rest_stats_new")],
        ])
    if role == "admin":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Barcha buyurtmalar", callback_data="admin_orders")],
            [InlineKeyboardButton("🏪 Restoranlar", callback_data="admin_rests")],
            [InlineKeyboardButton("🚴 Kuryerlar", callback_data="admin_couriers")],
            [InlineKeyboardButton("👥 Mijozlar", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        ])
    # mijoz
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍔 Buyurtma berish", callback_data="client_order")],
        [InlineKeyboardButton("📦 Mening buyurtmalarim", callback_data="client_my")],
        [InlineKeyboardButton("🏪 Restoran sifatida ro'yxatdan o'tish", callback_data="register_rest")],
        [InlineKeyboardButton("🚴 Kuryer sifatida ro'yxatdan o'tish", callback_data="register_courier")],
    ])

async def send_new_window(update, context, text, reply_markup=None):
    """YANGI OYNA: eski panel xabarini o'chirib, bitta yangi xabar yuboradi.
    Mijoz panelida oldingi operatsiyalar ko'rinmasligi uchun."""
    # Eski bot xabarini o'chirishga urinamiz
    old_id = context.user_data.get("panel_msg_id") if context else None
    chat_id = update.effective_chat.id if update.effective_chat else None
    if old_id and chat_id:
        try: await context.bot.delete_message(chat_id=chat_id, message_id=old_id)
        except: pass
    # Yangi xabar
    try:
        if update.callback_query:
            # Callback bo'lsa - eski xabarni o'chirib yangisini yuboramiz (edit emas, toza oyna)
            try: await update.callback_query.message.delete()
            except: pass
            m = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        else:
            m = await update.message.reply_text(text, reply_markup=reply_markup)
        if context is not None:
            context.user_data["panel_msg_id"] = m.message_id
        return m
    except Exception:
        return None

async def show_main(update, user_id, text="Asosiy menyu:"):
    u = DB["users"].get(str(user_id), {})
    role = u.get("role", "client")
    kb = main_kb(role)
    # YANGI OYNA: mijozda eski panelni o'chirib yangisini chiqaramiz
    try:
        ctx = None
        # context ni update dan olishga urinamiz - callback bo'lsa ham, message bo'lsa ham
        # show_main ga context kelmaydi, shuning uchun to'g'ridan-to'g'ri edit/delete qilamiz
        if update.callback_query:
            try: await update.callback_query.message.delete()
            except: pass
            await update.callback_query.message.reply_text(text, reply_markup=kb)
        else:
            await update.message.reply_text(text, reply_markup=kb)
    except Exception:
        pass

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
    await show_main(update, update.effective_user.id, f"Salom {u['name']}! 👋\n\nSizning rolingiz: {u['role']} 🔒")

async def set_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    role = q.data.replace("setrole_", "")
    uid = str(q.from_user.id)
    # SUPER ADMIN - hammasiga o'ta oladi
    if q.from_user.id == SUPER_ADMIN:
        DB["users"][uid]["role"] = role; save()
        await show_main(update, q.from_user.id, f"Rol o'zgardi: {role} ✅")
        return
    # QULF: oddiy odam faqat o'zi ro'yxatdan o'tgan rolga o'ta oladi
    u = DB["users"].get(uid, {})
    has_rest = any(v.get("admin") == q.from_user.id for v in DB["restaurants"].values())
    has_courier = bool(u.get("courier_registered"))
    allowed = False
    if role == "client": allowed = True  # hamma mijoz bo'la oladi
    if role == "restaurant" and has_rest: allowed = True
    if role == "courier" and has_courier: allowed = True
    if role == "admin": allowed = False
    if not allowed:
        if role == "restaurant":
            await q.edit_message_text("❌ Siz restoran sifatida ro'yxatdan o'tmagansiz.\n\nAvval restoran sifatida ro'yxatdan o'ting, keyin panelga kirasiz.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 Restoran sifatida ro'yxatdan o'tish", callback_data="register_rest")],[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
        elif role == "courier":
            await q.edit_message_text("❌ Siz kuryer sifatida ro'yxatdan o'tmagansiz.\n\nAvval kuryer sifatida ro'yxatdan o'ting.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚴 Kuryer sifatida ro'yxatdan o'tish", callback_data="register_courier")],[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
        else:
            await q.answer("Bu rol sizda yo'q", show_alert=True)
        return
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
    # ROL QULFLANGAN: bevosita rol almashtirib bo'lmaydi - faqat qayta ro'yxatdan o'tish orqali
    cur = DB["users"].get(str(uid), {}).get("role", "client")
    await q.edit_message_text(f"🔒 Rolsiz qulflangan: {cur}\n\nRolni bevosita o'zgartirib bo'lmaydi.\nBoshqa rolga o'tmoqchi bo'lsangiz - o'sha rol sifatida qaytadan ro'yxatdan o'ting:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏪 Restoran sifatida ro'yxatdan o'tish", callback_data="register_rest")],
            [InlineKeyboardButton("🚴 Kuryer sifatida ro'yxatdan o'tish", callback_data="register_courier")],
            [InlineKeyboardButton("🍔 Mijoz sifatida davom etish", callback_data="setrole_client")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")],
        ]))



async def rest_card_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key, r = _my_rest(q.from_user.id)
    if not r: return
    context.user_data["step"] = "rest_card_val"
    await q.edit_message_text(f"💳 Hozirgi kartangiz: {r.get('payme_card','belgilanmagan')}\n\nYangi karta raqamini yozing:\nMasalan: 8600123456789012",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="rest_panel")]]))

# --- RESTORAN O'ZI RO'YXATDAN O'TISHI ---
async def register_rest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    # Oldin ro'yxatdan o'tganmi? - o'zining restorani bormi tekshiramiz
    my = [k for k,v in DB["restaurants"].items() if v.get("admin") == q.from_user.id]
    if my:
        names = ", ".join([DB["restaurants"][k]["name"] for k in my])
        await q.edit_message_text(f"✅ Sizda allaqachon restoran bor: {names}\n\nUni boshqarish uchun Rolni o'zgartirish -> Restoran ni tanlang.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 Restoran panelimga kirish", callback_data="setrole_restaurant")],[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
        return
    context.user_data["step"] = "reg_name"
    context.user_data["reg"] = {}
    await q.edit_message_text("🏪 *Restoran ro'yxatdan o'tish*\n\n1-qadam: Restoraningiz nomini yozing:\nMasalan: Diplomat Restaurant",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="back_main")]]), parse_mode="Markdown")

async def register_rest_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["step"] = None
    context.user_data.pop("reg", None)
    await show_main(update, q.from_user.id, "Bekor qilindi.")

def _slug(name: str):
    import re
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9_]+", "_", s).strip("_")
    return s[:20] or "rest"

# on_text ichida reg_* steplarni ushlash uchun yordamchi - on_text ning boshiga qo'shiladi
async def handle_reg_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if not step or not step.startswith("reg_"):
        return False
    text = (update.message.text or "").strip()
    reg = context.user_data.get("reg", {})
    if step == "reg_name":
        if len(text) < 3:
            await update.message.reply_text("❌ Nom juda qisqa. Qaytadan yozing:")
            return True
        reg["name"] = text
        context.user_data["reg"] = reg
        context.user_data["step"] = "reg_menu"
        await update.message.reply_text("✅ Nom saqlandi: " + text + "\n\n2-qadam: Menyuni yozing - har bir qatorga 1 ta taom:\n\n*Namuna:*\nOsh - 35000\nShashlik - 45000\nLavash - 38000\n\nKamida 1 ta taom yozing, keyin yuboring:", parse_mode="Markdown")
        return True
    if step == "reg_menu":
        menu = {}
        for line in text.split("\n"):
            line=line.strip()
            if not line: continue
            if "-" in line:
                n, pr = line.rsplit("-", 1)
                n=n.strip(); pr=pr.strip().replace(" ", "").replace("so'm","").replace("som","")
                try: menu[n]=int(pr)
                except: pass
        if not menu:
            await update.message.reply_text("❌ Tushunmadim. Masalan shunday yozing:\nOsh - 35000\nShashlik - 45000")
            return True
        reg["menu"] = menu
        context.user_data["reg"] = reg
        context.user_data["step"] = "reg_delivery"
        await update.message.reply_text(f"✅ Menyu saqlandi: {len(menu)} ta taom.\n\n3-qadam: Yetkazib berish narxini yozing (faqat raqam, so'mda):\nMasalan: 15000\n100 000 dan yuqoriga bepul bo'ladi.")
        return True
    if step == "reg_delivery":
        try: delivery = int(text.replace(" ","").replace("so'm",""))
        except:
            await update.message.reply_text("❌ Faqat raqam yozing. Masalan: 15000")
            return True
        reg["delivery"] = delivery
        context.user_data["reg"] = reg
        context.user_data["step"] = "reg_phone"
        await update.message.reply_text("✅ Yetkazish narxi saqlandi.\n\n4-qadam: Telefon raqamingizni yuboring - pastdagi tugmani bosing 👇",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
        return True
    return False

async def finish_reg_with_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # on_contact dan chaqiriladi, agar step == reg_phone bo'lsa
    reg = context.user_data.get("reg", {})
    if not reg or not reg.get("name"):
        return False
    uid = update.effective_user.id
    key = _slug(reg["name"])
    base = key; i = 2
    while key in DB["restaurants"]:
        key = f"{base}_{i}"; i+=1
    DB["restaurants"][key] = {"name": reg["name"], "admin": uid, "delivery": reg.get("delivery", 15000), "menu": reg.get("menu", {}), "active": True, "phone": DB["users"].get(str(uid), {}).get("phone","")}
    save()
    # Avtomatik rolini restoran qilamiz
    DB["users"][str(uid)]["role"] = "restaurant"; save()
    context.user_data["step"] = None
    context.user_data.pop("reg", None)
    await update.message.reply_text(f"🎉 *Tabriklaymiz! Restoraningiz ro'yxatdan o'tdi!*\n\n🏪 {reg['name']}\n🍔 {len(reg.get('menu',{}))} ta taom\n🚚 Yetkazish: {reg.get('delivery',15000):,} so'm\n\nEndi mijozlar sizni ro'yxatda ko'radi. Buyurtma tushsa shu yerga keladi.\nMenyuni o'zgartirish uchun: Restoran panelingizni oching",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 Restoran panelim", callback_data="setrole_restaurant")]]))
    # Super adminga xabar
    try: await context.bot.send_message(chat_id=SUPER_ADMIN, text=f"🆕 Yangi restoran ro'yxatdan o'tdi!\n🏪 {reg['name']}\n👤 {update.effective_user.first_name} | ID: {uid}\n📞 {DB['users'].get(str(uid),{}).get('phone','')}")
    except: pass
    return True


# --- RESTORAN EGASI PANELI: menyu / narx / tugadi / ochiq-yopiq / yetkazish ---
def _my_rest(uid):
    for k,v in DB["restaurants"].items():
        if v.get("admin") == uid:
            return k, v
    return None, None

async def rest_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key, r = _my_rest(q.from_user.id)
    if not r:
        await q.edit_message_text("❌ Sizda restoran yo'q. Avval ro'yxatdan o'ting.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ Ro'yxatdan o'tish", callback_data="register_rest")],[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
        return
    sold = r.get("sold_out", [])
    status = "🟢 OCHIQ" if r.get("active", True) else "🔴 YOPIQ"
    txt = f"🏪 *{r['name']}*\n\nHolat: {status}\n🚚 Yetkazish: {r.get('delivery',15000):,} so'm\n🍔 Taomlar: {len(r.get('menu',{}))} ta\n❌ Tugagan: {len(sold)} ta\n\nNimani o'zgartirmoqchisiz?"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yangi taom qo'shish", callback_data="rest_add")],
        [InlineKeyboardButton("💰 Narxni o'zgartirish", callback_data="rest_price_list")],
        [InlineKeyboardButton("❌ Tugadi / Bor qilish", callback_data="rest_menu")],
        [InlineKeyboardButton("🚚 Yetkazish narxini o'zgartirish", callback_data="rest_delivery")],
        [InlineKeyboardButton("💳 Payme / Click karta raqamim", callback_data="rest_card")],
        [InlineKeyboardButton("🟢 Ochiq / 🔴 Yopiq", callback_data="rest_open")],
        [InlineKeyboardButton("📊 Bugungi statistika", callback_data="rest_stats_new")],
        [InlineKeyboardButton("⬅️ Asosiy", callback_data="back_main")],
    ])
    await q.edit_message_text(txt, reply_markup=kb, parse_mode="Markdown")

async def rest_menu_manage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key, r = _my_rest(q.from_user.id)
    if not r:
        await q.edit_message_text("Restoran topilmadi.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]])); return
    sold = set(r.get("sold_out", []))
    kb=[]
    for n, pr in r.get("menu", {}).items():
        mark = "❌ TUGADI" if n in sold else "✅ Bor"
        kb.append([InlineKeyboardButton(f"{n} - {pr:,} | {mark}", callback_data=f"rest_toggle_{n}")])
    kb.append([InlineKeyboardButton("➕ Yangi taom", callback_data="rest_add")])
    kb.append([InlineKeyboardButton("💰 Narxni o'zgartirish", callback_data="rest_price_list")])
    kb.append([InlineKeyboardButton("⬅️ Panel", callback_data="rest_panel")])
    await q.edit_message_text(f"🍔 *{r['name']} - Menyu*\n\nTaomni bossangiz Tugadi/Bor almashadi. Narxni o'zgartirish uchun pastdagi tugmani bosing.",
        reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def rest_toggle_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    name = q.data.replace("rest_toggle_", "", 1)
    key, r = _my_rest(q.from_user.id)
    if not r: return
    sold = r.setdefault("sold_out", [])
    if name in sold: sold.remove(name); await q.answer(f"✅ {name} endi bor")
    else: sold.append(name); await q.answer(f"❌ {name} tugadi deb belgilandi")
    save()
    await rest_menu_manage(update, context)

async def rest_price_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key, r = _my_rest(q.from_user.id)
    kb=[]
    for n, pr in r.get("menu", {}).items():
        kb.append([InlineKeyboardButton(f"{n} - {pr:,}", callback_data=f"rest_price_{n}")])
    kb.append([InlineKeyboardButton("⬅️ Panel", callback_data="rest_panel")])
    await q.edit_message_text("Qaysi taomning narxini o'zgartirasiz?", reply_markup=InlineKeyboardMarkup(kb))

async def rest_price_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    name = q.data.replace("rest_price_", "", 1)
    context.user_data["step"] = "rest_price_val"
    context.user_data["edit_name"] = name
    await q.edit_message_text(f"💰 *{name}* uchun yangi narxni yozing (faqat raqam):\nMasalan: 40000",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="rest_panel")]]), parse_mode="Markdown")

async def rest_add_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["step"] = "rest_add"
    await q.edit_message_text("➕ *Yangi taom qo'shish*\n\nShunday yozing:\n`Osh - 35000`\nBir xabarda bir nechta ham bo'ladi:\n`Osh - 35000\\nShashlik - 45000`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="rest_panel")]]), parse_mode="Markdown")

async def rest_delivery_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["step"] = "rest_delivery_val"
    await q.edit_message_text("🚚 Yangi yetkazib berish narxini yozing (faqat raqam):\nMasalan: 12000",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="rest_panel")]]))

async def rest_open_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key, r = _my_rest(q.from_user.id)
    if not r: return
    r["active"] = not r.get("active", True); save()
    await q.answer("🟢 Restoran ochildi" if r["active"] else "🔴 Restoran yopildi")
    await rest_panel(update, context)

async def rest_stats_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key, r = _my_rest(q.from_user.id)
    if not r:
        await q.edit_message_text("Restoran topilmadi.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]])); return
    my_orders = [o for o in DB["orders"].values() if o.get("cafe") == key]
    done = [o for o in my_orders if o.get("status") == "done"]
    waiting = [o for o in my_orders if o.get("status") in ("waiting","to_courier","taken")]
    total = sum(o.get("total",0) for o in done)
    txt = f"📊 *{r['name']} - Statistika*\n\n📦 Jami buyurtma: {len(my_orders)}\n✅ Yetkazilgan: {len(done)}\n⏳ Kutilmoqda: {len(waiting)}\n💰 Yetkazilganlardan savdo: {total:,} so'm\n\n*Oxirgi 5 ta:*\n"
    for o in my_orders[-5:]:
        txt += f"#{o['id']} | {o.get('status')} | {o.get('total',0):,} so'm\n"
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Panel", callback_data="rest_panel")]]), parse_mode="Markdown")

async def handle_rest_panel_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if not step or not step.startswith("rest_"):
        return False
    text = (update.message.text or "").strip()
    key, r = _my_rest(update.effective_user.id)
    if not r:
        await update.message.reply_text("Avval restoran ro'yxatdan o'tkazing.")
        context.user_data["step"]=None; return True
    if step == "rest_add":
        menu = {}
        for line in text.split("\n"):
            line=line.strip()
            if not line or "-" not in line: continue
            n, pr = line.rsplit("-",1); n=n.strip(); pr=pr.strip().replace(" ","").replace("so'm","")
            try: menu[n]=int(pr)
            except: pass
        if not menu:
            await update.message.reply_text("❌ Tushunmadim. Masalan: Osh - 35000"); return True
        r.setdefault("menu", {}).update(menu); save()
        context.user_data["step"]=None
        await update.message.reply_text(f"✅ Qo'shildi: {', '.join(menu.keys())}\nHozir menyuda {len(r['menu'])} ta taom bor.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 Panelga qaytish", callback_data="rest_panel")]]))
        return True
    if step == "rest_price_val":
        try: price=int(text.replace(" ","").replace("so'm",""))
        except:
            await update.message.reply_text("❌ Faqat raqam yozing. Masalan: 40000"); return True
        name = context.user_data.get("edit_name")
        if name in r.get("menu", {}):
            r["menu"][name]=price; save()
            context.user_data["step"]=None
            await update.message.reply_text(f"✅ {name} narxi {price:,} so'm ga o'zgardi.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 Panelga qaytish", callback_data="rest_panel")]]))
        else:
            await update.message.reply_text("Taom topilmadi."); context.user_data["step"]=None
        return True
    if step == "rest_card_val":
        card = text.replace(" ", "")
        if len(card) < 16 or not card.isdigit():
            await update.message.reply_text("❌ Karta 16 ta raqam bo'lishi kerak. Qaytadan yozing:"); return True
        # Chiroyli ko'rinishda saqlaymiz: 8600 1234 5678 9012
        pretty = " ".join([card[i:i+4] for i in range(0, len(card), 4)])
        r["payme_card"] = pretty; save(); context.user_data["step"]=None
        await update.message.reply_text(f"✅ Kartangiz saqlandi: {pretty}\nEndi mijozlarga shu karta chiqadi.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 Panelga qaytish", callback_data="rest_panel")]]))
        return True
    if step == "rest_delivery_val":
        try: d=int(text.replace(" ","").replace("so'm",""))
        except:
            await update.message.reply_text("❌ Faqat raqam yozing. Masalan: 12000"); return True
        r["delivery"]=d; save(); context.user_data["step"]=None
        await update.message.reply_text(f"✅ Yetkazish narxi {d:,} so'm ga o'zgardi. 100 000 dan yuqoriga bepul.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 Panelga qaytish", callback_data="rest_panel")]]))
        return True
    return False


# --- KURYER O'ZI RO'YXATDAN O'TISHI + O'Z BALANSI ---
async def register_courier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = str(q.from_user.id)
    u = DB["users"].get(uid, {})
    if u.get("courier_registered"):
        await courier_new(q, context, f"✅ Siz allaqachon kuryer sifatida ro'yxatdan o'tgansiz.\n\n🚴 Transport: {u.get('courier_transport','-')}\n📍 Hudud: {u.get('courier_area','-')}\n💰 Balans: {u.get('balance',0):,} so'm",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚴 Kuryer panelim", callback_data="courier_panel")],[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
        return
    context.user_data["step"] = "regcourier_transport"
    context.user_data["reg_courier"] = {}
    _m = await courier_new(q, context, "🚴 *Kuryer sifatida ro'yxatdan o'tish*\n\n1-qadam: Transportingizni tanlang:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛵 Moped / Skuter", callback_data="courier_tr_moped")],
            [InlineKeyboardButton("🚗 Mashina", callback_data="courier_tr_car")],
            [InlineKeyboardButton("🚲 Velosiped", callback_data="courier_tr_bike")],
            [InlineKeyboardButton("🚶 Piyoda", callback_data="courier_tr_walk")],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data="back_main")],
        ]), parse_mode="Markdown")
    try: context.user_data["courier_panel_msg_id"] = _m.message_id
    except: pass

async def register_courier_transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    tr_map = {"courier_tr_moped":"🛵 Moped / Skuter","courier_tr_car":"🚗 Mashina","courier_tr_bike":"🚲 Velosiped","courier_tr_walk":"🚶 Piyoda"}
    tr = tr_map.get(q.data, "🛵 Moped")
    context.user_data["reg_courier"] = {"transport": tr}
    context.user_data["step"] = "regcourier_area"
    _m2 = await courier_new(q, context, f"✅ Transport: {tr}\n\n2-qadam: Qaysi hududda ishlaysiz? Yozing:\nMasalan: Yashil Bozor, 5-kichik daxa, Aeroport\nYoki: Butun Termiz",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="back_main")]]))
    try: context.user_data["courier_panel_msg_id"] = _m2.message_id
    except: pass

async def courier_new(q, context, text, reply_markup=None, parse_mode=None):
    """KURYER YANGI OYNA: eski oyna o'chadi, bitta yangi oyna qoladi."""
    try: await q.message.delete()
    except: pass
    _mm = await context.bot.send_message(chat_id=q.from_user.id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    try: context.user_data["courier_panel_msg_id"] = _mm.message_id
    except: pass
    return _mm

async def courier_msg_new(update, context, text, reply_markup=None, parse_mode=None):
    """Kuryer yozgan xabar (matn/kontakt) dan keyin - eski bot oynasi + mijoz yozgan xabar o'chadi."""
    old = context.user_data.get("courier_panel_msg_id")
    if old:
        try: await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=old)
        except: pass
    try: await update.message.delete()
    except: pass
    m = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    context.user_data["courier_panel_msg_id"] = m.message_id
    return m

async def courier_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = str(q.from_user.id); u = DB["users"].get(uid, {})
    if not u.get("courier_registered"):
        await courier_new(q, context, "❌ Avval kuryer sifatida ro'yxatdan o'ting.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚴 Ro'yxatdan o'tish", callback_data="register_courier")],[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]))
        return
    # LOGIN/PAROL TEKSHIRUVI: eski kuryerlarda login yo'q bo'lsa - bir marta o'rnatadi, yangilarida parol so'raydi
    if not u.get("courier_login"):
        context.user_data["step"] = "courier_set_login"
        await courier_new(q, context, "🔐 Xavfsizlik uchun login o'rnating!\n\nSiz eski ro'yxatdan o'tgansiz, loginingiz yo'q. Bir marta login o'ylab toping:\nMasalan: diyorbek01")
        return
    if not context.user_data.get("courier_logged_in"):
        context.user_data["step"] = "courier_login"
        await courier_new(q, context, f"🔐 Kirish kerak!\n\nLoginingiz: {u.get('courier_login')}\nLoginingizni qaytadan yozing (keyin parol so'rayman):")
        return
    my_taken = [o for o in DB["orders"].values() if o.get("courier_id")==q.from_user.id and o.get("status")=="taken"]
    my_done = [o for o in DB["orders"].values() if o.get("courier_id")==q.from_user.id and o.get("status")=="done"]
    status = "🟢 ONLINE" if u.get("online") else "🔴 OFFLINE"
    txt = f"🚴 *Mening kuryer panelim*\n🔐 Login: {u.get('courier_login','-')}\n\nHolat: {status}\n🚗 Transport: {u.get('courier_transport','-')}\n📍 Hudud: {u.get('courier_area','-')}\n📞 Tel: {u.get('phone','-')}\n\n💰 Balans: {u.get('balance',0):,} so'm\n✅ Yetkazgan: {u.get('delivered',0)} ta ({len(my_done)} ta shu yerda)\n🚴 Hozir olib ketayotgan: {len(my_taken)} ta"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 ONLINE / 🔴 OFFLINE", callback_data="courier_toggle")],
        [InlineKeyboardButton("📦 Bo'sh buyurtmalar", callback_data="courier_list")],
        [InlineKeyboardButton("🚴 Mening buyurtmam", callback_data="courier_my")],
        [InlineKeyboardButton("💰 Pulni yechib olish (so'rov)", callback_data="courier_withdraw")],
        [InlineKeyboardButton("✏️ Transport / Hududni o'zgartirish", callback_data="courier_edit")],
        [InlineKeyboardButton("⬅️ Asosiy", callback_data="back_main")],
    ])
    await courier_new(q, context, txt, reply_markup=kb, parse_mode="Markdown")

async def courier_balance_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = str(q.from_user.id); u = DB["users"].get(uid, {})
    my_done = [o for o in DB["orders"].values() if o.get("courier_id")==q.from_user.id and o.get("status")=="done"]
    txt = f"💰 *Mening hisobim*\n\nBalans: {u.get('balance',0):,} so'm\n✅ Yetkazgan: {u.get('delivered',0)} ta\n\n*Oxirgi yetkazganlarim:*\n"
    for o in my_done[-5:]:
        txt += f"#{o['id']} | {o.get('total',0):,} so'm | +15 000 ga yaqin\n"
    txt += "\nHar bir yetkazilgan buyurtma uchun +15 000 so'm (yoki restoran yetkazish narxi) qo'shiladi."
    await courier_new(q, context, txt, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Pulni yechish so'rovi", callback_data="courier_withdraw")],
        [InlineKeyboardButton("⬅️ Panel", callback_data="courier_panel")],
    ]), parse_mode="Markdown")

async def courier_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = str(q.from_user.id); u = DB["users"].get(uid, {})
    bal = u.get("balance", 0)
    # TUZATILDI: oldin 30 000 edi, endi 1 ta yetkazish (15 000) dan ham yechish mumkin
    # Agar balans 0 bo'lsa - aniq yozuv bilan tushuntiramiz, faqat alert emas
    if bal <= 0:
        await courier_new(q, context, f"💰 Balansingiz: 0 so'm\n\nHali pul yechib bo'lmaydi - avval buyurtma yetkazib pul ishlang.\nHar bir yetkazish uchun +15 000 so'm qo'shiladi.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📦 Bo'sh buyurtmalar", callback_data="courier_list")],[InlineKeyboardButton("⬅️ Panel", callback_data="courier_panel")]]))
        return
    context.user_data["step"] = "courier_withdraw_card"
    context.user_data["withdraw_amount"] = bal
    await courier_new(q, context, f"💰 Balansingiz: {bal:,} so'm\n\nPulni qaysi kartaga o'tkazaylik? Karta raqamini yozing (16 ta raqam):\nMasalan: 8600 1234 5678 9012\n\nSo'rov yuboriladi, admin to'lab beradi.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="courier_panel")]]))

async def courier_withdraw_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Faqat Super Admin bosadi - balansni nollaydi, kuryerga xabar yuboradi
    q = update.callback_query; await q.answer()
    if q.from_user.id != SUPER_ADMIN:
        await q.answer("Faqat admin tasdiqlay oladi", show_alert=True); return
    try: _, uid, amount = q.data.split("_"); amount = int(amount)
    except: return
    u = DB["users"].get(str(uid))
    if not u: await q.answer("Kuryer topilmadi"); return
    # Balansni nollaymiz
    u["balance"] = 0; save()
    await _edit_q(q, f"✅ To'landi!\n🚴 Kuryer: {u.get('name')} | ID: {uid}\n💰 {amount:,} so'm - balans nolga tushdi.")
    try: await context.bot.send_message(chat_id=int(uid), text=f"✅ Pul yechish tasdiqlandi!\n\n💰 {amount:,} so'm kartangizga o'tkazildi.\nBalansingiz endi 0 so'm. Ishlashda davom eting! 🚴")
    except: pass

async def courier_withdraw_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.from_user.id != SUPER_ADMIN:
        await q.answer("Faqat admin", show_alert=True); return
    try: _, uid, amount = q.data.split("_")
    except: return
    await _edit_q(q, f"❌ So'rov rad etildi. Kuryer ID: {uid}, summa: {amount}")
    try: await context.bot.send_message(chat_id=int(uid), text="❌ Pul yechish so'rovingiz rad etildi. Admin bilan bog'laning.")
    except: pass

async def courier_edit_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["step"] = "courier_edit_area"
    await courier_new(q, context, "✏️ Yangi hududingizni yozing:\nMasalan: Yashil Bozor, Aeroport",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="courier_panel")]]))

async def handle_courier_reg_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if not step or not step.startswith("regcourier") and not step.startswith("courier_"):
        return False
    text = (update.message.text or "").strip()
    uid = str(update.effective_user.id)
    # 1. Hudud
    if step == "regcourier_area":
        rc = context.user_data.get("reg_courier", {})
        rc["area"] = text
        context.user_data["reg_courier"] = rc
        context.user_data["step"] = "regcourier_phone"
        await courier_msg_new(update, context, f"✅ Hudud: {text}\n\n3-qadam: Telefon raqamingizni yuboring 👇",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
        return True
    if step == "courier_edit_area":
        DB["users"][uid]["courier_area"] = text; save()
        context.user_data["step"] = None
        await courier_msg_new(update, context, f"✅ Hududingiz o'zgardi: {text}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚴 Panelga qaytish", callback_data="courier_panel")]]))
        return True
    if step == "courier_withdraw_card":
        card = text.replace(" ", "")
        if len(card) < 16 or not card.isdigit():
            await courier_msg_new(update, context, "❌ Karta raqami 16 ta raqam bo'lishi kerak. Qaytadan yozing:"); return True
        u = DB["users"][uid]; bal = u.get("balance", 0)
        # So'rovni Super Adminga yuboramiz, balansni nolga tushirmaymiz - admin tasdiqlagach to'lanadi
        try: await context.bot.send_message(chat_id=SUPER_ADMIN, text=f"💸 *PUL YECHISH SO'ROVI*\n\n🚴 Kuryer: {u.get('name')} | ID: {uid}\n📞 {u.get('phone')}\n💰 Summa: {bal:,} so'm\n💳 Karta: {card[:4]} **** **** {card[-4:]}\n\nTo'laganingizdan keyin kuryer balansini qo'lda nollang.",
                parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ TO'LADIM - Tasdiqlash", callback_data=f"wdok_{uid}_{bal}"), InlineKeyboardButton("❌ Rad etish", callback_data=f"wdno_{uid}_{bal}")]]))
        except: pass
        context.user_data["step"] = None
        await courier_msg_new(update, context, f"✅ So'rovingiz yuborildi!\n💰 {bal:,} so'm\n💳 Karta: **** {card[-4:]}\n\nAdmin tez orada to'laydi, to'langach sizga xabar keladi.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚴 Panelga qaytish", callback_data="courier_panel")]]))
        return True
    # --- LOGIN / PAROL: ro'yxatdan o'tishda ---
    if step == "regcourier_login":
        login = text.lower().replace(" ", "").replace("@", "")
        if len(login) < 4 or len(login) > 20 or not login.replace("_", "").replace(".", "").isalnum():
            await courier_msg_new(update, context, "❌ Login noto'g'ri!\n\nFaqat lotin harf + raqam, 4-20 ta belgi. Masalan: diyorbek01\nQaytadan yozing:")
            return True
        # Boshqa kuryerda bormi?
        for _uid2, _u2 in DB["users"].items():
            if _uid2 != uid and _u2.get("courier_login") == login:
                await courier_msg_new(update, context, f"❌ '{login}' logini band! Boshqa login tanlang:")
                return True
        rc = context.user_data.get("reg_courier", {}); rc["login"] = login; context.user_data["reg_courier"] = rc
        context.user_data["step"] = "regcourier_password"
        await courier_msg_new(update, context, f"✅ Login: {login}\n\n5-qadam: Parol o'ylab toping (kamida 4 ta belgi):\nMasalan: 1234 yoki diyor2024\n\n⚠️ Parolni hech kimga bermang! Yozgan xabaringiz o'chib ketadi.")
        return True
    if step == "regcourier_password":
        if len(text) < 4:
            await courier_msg_new(update, context, "❌ Parol kamida 4 ta belgi bo'lishi kerak. Qaytadan yozing:")
            return True
        rc = context.user_data.get("reg_courier", {}); rc["pass_hash"] = courier_pass_hash(text); context.user_data["reg_courier"] = rc
        # Ro'yxatni yakunlaymiz - finish funksiyasi endi login/parol bilan saqlaydi
        await finish_courier_reg_with_phone(update, context)
        return True
    # --- KIRISH (LOGIN): panel ochishda parol so'rash ---
    if step == "courier_login":
        login = text.lower().replace(" ", "").replace("@", "")
        # Shu Telegram ID dagi kuryerning logini shu bo'lishi kerak
        u_now = DB["users"].get(uid, {})
        if u_now.get("courier_login") and u_now.get("courier_login") != login:
            await courier_msg_new(update, context, "❌ Bu login sizniki emas! O'z loginingizni yozing:")
            return True
        context.user_data["login_try"] = login
        context.user_data["step"] = "courier_login_pass"
        await courier_msg_new(update, context, f"🔐 Login: {login}\n\nParolingizni yozing:")
        return True
    if step == "courier_login_pass":
        u_now = DB["users"].get(uid, {})
        if u_now.get("courier_pass_hash") and courier_pass_hash(text) == u_now.get("courier_pass_hash"):
            context.user_data["courier_logged_in"] = True
            context.user_data["step"] = None
            await courier_msg_new(update, context, f"✅ Xush kelibsiz, {u_now.get('name','Kuryer')}! Kirish muvaffaqiyatli.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚴 Kuryer panelim", callback_data="courier_panel")]]))
        else:
            await courier_msg_new(update, context, "❌ Parol xato! Qaytadan yozing:")
        return True
    # --- ESKI KURYERLARGA LOGIN/PAROL O'RNATISH (bir marta) ---
    if step == "courier_set_login":
        login = text.lower().replace(" ", "").replace("@", "")
        if len(login) < 4:
            await courier_msg_new(update, context, "❌ Login kamida 4 ta belgi bo'lsin. Qaytadan yozing:")
            return True
        context.user_data["set_login"] = login
        context.user_data["step"] = "courier_set_pass"
        await courier_msg_new(update, context, f"✅ Login: {login}\n\nEndi parol o'ylab toping (kamida 4 ta belgi):")
        return True
    if step == "courier_set_pass":
        if len(text) < 4:
            await courier_msg_new(update, context, "❌ Parol kamida 4 ta belgi bo'lishi kerak. Qaytadan yozing:")
            return True
        u_now = DB["users"].get(uid, {})
        u_now["courier_login"] = context.user_data.get("set_login", "")
        u_now["courier_pass_hash"] = courier_pass_hash(text)
        save()
        context.user_data["courier_logged_in"] = True
        context.user_data["step"] = None
        await courier_msg_new(update, context, f"✅ Login va parol o'rnatildi!\n🔐 Login: {u_now['courier_login']}\n\nEndi panel har safar shu parol bilan ochiladi.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚴 Kuryer panelim", callback_data="courier_panel")]]))
        return True
    return False

async def finish_courier_reg_with_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") != "regcourier_phone":
        return False
    rc = context.user_data.get("reg_courier", {})
    uid = str(update.effective_user.id)
    DB["users"][uid]["role"] = "courier"
    DB["users"][uid]["courier_registered"] = True
    DB["users"][uid]["courier_transport"] = rc.get("transport", "🛵 Moped")
    DB["users"][uid]["courier_area"] = rc.get("area", "Termiz")
    if "balance" not in DB["users"][uid]: DB["users"][uid]["balance"] = 0
    if "delivered" not in DB["users"][uid]: DB["users"][uid]["delivered"] = 0
    save()
    # Agar login hali o'rnatilmagan bo'lsa - avval login/parol so'raymiz, tugatmaymiz
    if not context.user_data.get("reg_courier", {}).get("login"):
        context.user_data["step"] = "regcourier_login"
        await courier_msg_new(update, context, f"✅ Telefon qabul qilindi!\n\n4-qadam: LOGIN o'ylab toping\nBu sizning kuryer loginingiz bo'ladi. Har safar panelga shu login + parol bilan kirasiz.\n\nMasalan: diyorbek01\nLoginingizni yozing:")
        return True
    # Login/parol ham tayyor - endi yakunlaymiz
    _rc2 = context.user_data.get("reg_courier", {})
    DB["users"][uid]["courier_login"] = _rc2.get("login", "")
    DB["users"][uid]["courier_pass_hash"] = _rc2.get("pass_hash", "")
    save()
    context.user_data["step"] = None
    context.user_data["courier_logged_in"] = True
    context.user_data.pop("reg_courier", None)
    await courier_msg_new(update, context, f"🎉 *Tabriklaymiz! Kuryer sifatida ro'yxatdan o'tdingiz!*\n\n🔐 Loginingiz: {DB['users'][uid].get('courier_login')}\n⚠️ Parolingizni eslab qoling! Panel har safar shu parol bilan ochiladi.\n\n🚗 Transport: {rc.get('transport')}\n📍 Hudud: {rc.get('area')}\n\nEndi ONLINE bo'ling - buyurtmalar sizga keladi. Har bir yetkazgan buyurtma uchun hisobingizga pul qo'shiladi.",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚴 Kuryer panelim", callback_data="courier_panel")]]))
    try: await context.bot.send_message(chat_id=SUPER_ADMIN, text=f"🆕 Yangi kuryer ro'yxatdan o'tdi!\n🚴 {update.effective_user.first_name} | ID: {uid}\n🔐 Login: {DB['users'][uid].get('courier_login','-')} (parol kuryerda)\n🚗 {rc.get('transport')} | 📍 {rc.get('area')}\n📞 {DB['users'][uid].get('phone','')}")
    except: pass
    return True

# --- MIJOZ ---
async def client_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    kb = [[InlineKeyboardButton(r["name"], callback_data=f"cafe_{key}")] for key, r in DB["restaurants"].items() if r.get("active")]
    kb.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")])
    try: await q.message.delete()
    except: pass
    await context.bot.send_message(chat_id=q.from_user.id, text="Qaysi restorandan buyurtma berasiz?", reply_markup=InlineKeyboardMarkup(kb))

async def cafe_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key = q.data.replace("cafe_", "", 1)
    context.user_data["cafe"] = key
    context.user_data["cart"] = []
    r = DB["restaurants"][key]
    _sold = set(r.get("sold_out", []))
    kb = []
    for n, p in r["menu"].items():
        if n in _sold:
            kb.append([InlineKeyboardButton(f"❌ {n} - Tugadi", callback_data="sold_out_noop")])
        else:
            kb.append([InlineKeyboardButton(f"{n} - {p} so'm", callback_data=f"add_{n}_{p}")])
    kb.append([InlineKeyboardButton("✅ Savatni tasdiqlash", callback_data="confirm_cart")])
    kb.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="client_order")])
    _del = r.get("delivery", 15000)
    try: await q.message.delete()
    except: pass
    await context.bot.send_message(chat_id=q.from_user.id, text=f"🏪 {r['name']}\n⏱ Yetkazish: {_del:,} so\'m (100 000 dan yuqoriga BEPUL)\nMenyu:", reply_markup=InlineKeyboardMarkup(kb))

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
    # YANGI OYNA: eski panelni o'chirib, faqat bitta yangi oyna qoldiramiz
    try: await q.message.delete()
    except: pass
    await context.bot.send_message(chat_id=q.from_user.id, text="📞 Telefon raqamingizni yuboring 👇\n\nPastdagi tugmani bosing:", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
async def pay_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == "pay_naqd":
        context.user_data["payment"] = "Naqd 💵"
    elif q.data == "pay_payme":
        context.user_data["payment"] = "Payme 💳"
    else:
        context.user_data["payment"] = "Click 💳"
    context.user_data["step"] = "address"
    # YANGI OYNA: eski to'lov oynasini o'chirib, faqat manzil oynasi qoladi
    try: await q.message.delete()
    except: pass
    _m = await context.bot.send_message(chat_id=q.from_user.id, text="📍 Manzilingizni yozing (Masalan: Yashil Bozor, 5-uy):", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]], resize_keyboard=True, one_time_keyboard=True))
    context.user_data["panel_msg_id"] = _m.message_id
async def on_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.contact:
        return
    uid = str(update.effective_user.id)
    if uid not in DB["users"]:
        DB["users"][uid] = {"name": update.effective_user.first_name or "Mijoz", "role": "client", "phone": "", "online": False, "balance": 0, "delivered": 0}
    DB["users"][uid]["phone"] = update.message.contact.phone_number; save()
    step = context.user_data.get("step")
    if step == "regcourier_phone":
        await finish_courier_reg_with_phone(update, context)
        return
    if step == "reg_phone":
        await finish_reg_with_phone(update, context)
        return
    if step == "phone":
        if not context.user_data.get("cart"):
            context.user_data["step"] = None
            await show_main(update, update.effective_user.id, "✅ Raqamingiz qabul qilindi! Endi buyurtma berishingiz mumkin.\n\n🍔 Buyurtma berish uchun restoranni tanlang:")
            return
        context.user_data["step"] = "payment"
        # YANGI OYNA: eski raqam oynasini o'chirib, faqat to'lov oynasi qoladi
        try: await update.message.delete()
        except: pass
        await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Raqamingiz qabul qilindi!\n\n💳 To'lov turini tanlang:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💵 Naqd", callback_data="pay_naqd"), InlineKeyboardButton("💳 Click", callback_data="pay_click"), InlineKeyboardButton("💳 Payme", callback_data="pay_payme")]]))
        return
    if step == "courier_phone":
        context.user_data["step"] = None
        await update.message.reply_text("✅ Raqamingiz qabul qilindi! Endi ONLINE bo'ling.", reply_markup=ReplyKeyboardRemove())
        await show_main(update, update.effective_user.id)
        return
    context.user_data["step"] = None
    await show_main(update, update.effective_user.id, "✅ Raqamingiz qabul qilindi! Endi buyurtma berishingiz mumkin.\n\n🍔 Buyurtma berish uchun restoranni tanlang:")

async def send_phone_btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.message.reply_text("Pastdagi tugmani bosib raqamingizni yuboring 👇", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await handle_reg_text(update, context):
        return
    if await handle_rest_panel_text(update, context):
        return
    if await handle_courier_reg_text(update, context):
        return
    if context.user_data.get("step") != "address":
         await show_main(update, update.effective_user.id, "🏠 Asosiy menyu:")
         return
    address = update.message.text
    # YANGI OYNA: eski manzil oynasini o'chirib, faqat bitta "Buyurtma yuborildi" oynasi qoladi
    _old = context.user_data.get("panel_msg_id")
    if _old:
        try: await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=_old)
        except: pass
    try: await update.message.delete()
    except: pass
    cart = context.user_data.get("cart", []); cafe_key = context.user_data.get("cafe")
    _sub = sum(p for _, p in cart)
    _del = DB["restaurants"][cafe_key].get("delivery", 15000)
    if _sub >= 100000: _del = 0
    total = _sub + _del
    context.user_data["delivery_fee"] = _del
    oid = DB["counter"]; DB["counter"] += 1
    uid = str(update.effective_user.id)
    payment = context.user_data.get("payment", "Naqd 💵")
    DB["orders"][str(oid)] = {"id": oid, "cafe": cafe_key, "cart": cart, "total": total, "payment": payment, "user_id": int(uid), "name": DB["users"][uid]["name"], "phone": DB["users"][uid].get("phone",""), "address": address, "status": "waiting", "courier_id": None, "created": "now"}
    save()
    context.user_data["step"] = None
    r = DB["restaurants"][cafe_key]
    text = f"🔥 YANGI BUYURTMA #{oid}!\n\n🏪 {r['name']}\n👤 {DB['users'][uid]['name']} | 📞 {DB['users'][uid].get('phone')}\n📍 {address}\n"
    for n, p in cart: text += f"🛒 {n} - {p}\n"
    text += f"\n🚗 Yetkazib berish: {context.user_data.get(chr(100)+chr(101)+chr(108)+chr(105)+chr(118)+chr(101)+chr(114)+chr(121)+chr(95)+chr(102)+chr(101)+chr(101), 0)} \n💰 JAMI: {total} so'm | {payment}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ QABUL QILISH", callback_data=f"accept_{oid}"), InlineKeyboardButton("❌ RAD ETISH", callback_data=f"reject_{oid}")]])
    await context.bot.send_message(chat_id=r["admin"], text=text, reply_markup=kb)
    await context.bot.send_message(chat_id=SUPER_ADMIN, text=text)
    # --- TO'LOV TASDIQI: Naqd bo'lmasa chek so'raymiz ---
    if payment in ("Payme 💳", "Click 💳"):
        # Restoranga avval "to'lov kutilmoqda" deb yozamiz - asl xabar yuqorida ketdi, endi qo'shimcha ogohlantirish
        try: await context.bot.send_message(chat_id=r["admin"], text=f"⏳ Buyurtma #{oid} - TO'LOV KUTILMOQDA\n{payment} tanlandi. Mijoz hozir chek yuboradi, chek kelgach QABUL QILISH ni bosing.")
        except: pass
        context.user_data["step"] = f"pay_proof_{oid}"
        context.user_data["pending_oid"] = oid
        # Karta raqamini ko'rsatamiz - egasi o'z kartasini keyin paneldan o'zgartira oladi
        card = r.get("payme_card", "8600 **** **** ****")
        _m2 = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Buyurtmangiz yuborildi!\n\n💳 *{payment} bilan to'lang:*\nKarta: `{card}`\nSumma: {total:,} so'm\n\nTo'lovni qilib bo'lgach, *chekni shu yerga rasm qilib yuboring* 📸\nChek kelmaguncha restoran buyurtmani qabul qilmaydi.",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Asosiy", callback_data="back_main")]]))
    else:
        _m2 = await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Buyurtmangiz yuborildi! Restoran tasdiqlashi kutilmoqda...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Asosiy", callback_data="back_main")]]))


# --- CHEK RASMINI QABUL QILISH ---
async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step", "")
    if not step or not str(step).startswith("pay_proof_"):
        # Boshqa rasm bo'lsa e'tibor bermaymiz
        return
    oid = str(step.replace("pay_proof_", ""))
    order = DB["orders"].get(oid)
    if not order:
        await update.message.reply_text("❌ Buyurtma topilmadi.")
        context.user_data["step"] = None
        return
    order["payment_proof"] = True
    order["payment_status"] = "chek_keldi"
    save()
    context.user_data["step"] = None
    r = DB["restaurants"].get(order["cafe"], {})
    # Chek rasmini restoranga + adminga yuboramiz
    caption = f"🧾 *TO'LOV CHEKI KELDI!*\n\nBuyurtma #{oid}\n🏪 {r.get('name','')}\n👤 {order.get('name')} | 📞 {order.get('phone')}\n💰 {order.get('total',0):,} so'm | {order.get('payment')}\n\nChekni tekshirib, QABUL QILISH ni bosing."
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ QABUL QILISH", callback_data=f"accept_{oid}"), InlineKeyboardButton("❌ RAD ETISH", callback_data=f"reject_{oid}")]])
    photo_id = update.message.photo[-1].file_id
    try: await context.bot.send_photo(chat_id=r.get("admin"), photo=photo_id, caption=caption, parse_mode="Markdown", reply_markup=kb)
    except Exception as e: print("Chek restoranga yuborilmadi:", e)
    try: await context.bot.send_photo(chat_id=SUPER_ADMIN, photo=photo_id, caption=caption, parse_mode="Markdown")
    except: pass
    # YANGI OYNA: eski "karta" oynasini o'chirib, faqat bitta oyna qoladi
    try: await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data.get("panel_msg_id"))
    except: pass
    try: await update.message.delete()
    except: pass
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Chekingiz yuborildi!\nRestoran chekni tekshirib, buyurtmangizni tasdiqlaydi.\nBuyurtma #{oid}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Asosiy", callback_data="back_main")]]))

# --- RESTORAN ---
async def _edit_q(q, text, reply_markup=None):
    # Rasmli xabar bo'lsa edit_message_text ishlamaydi - caption ni o'zgartiramiz
    try:
        if reply_markup: await q.edit_message_text(text, reply_markup=reply_markup)
        else: await q.edit_message_text(text)
    except Exception:
        try:
            if reply_markup: await q.edit_message_caption(caption=text, reply_markup=reply_markup)
            else: await q.edit_message_caption(caption=text)
        except Exception:
            try:
                if reply_markup: await q.message.reply_text(text, reply_markup=reply_markup)
                else: await q.message.reply_text(text)
            except: pass

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    action, oid = q.data.split("_"); oid = str(oid)
    order = DB["orders"].get(oid)
    if not order: await q.answer("Topilmadi"); return
    # QULF: allaqachon qabul qilingan / rad etilgan bo'lsa - 2-marta yubormaymiz
    if action == "accept" and order.get("status") in ("to_courier", "taken", "done"):
        await q.answer("Bu buyurtma allaqachon qabul qilingan ✅")
        await _edit_q(q, f"✅ Buyurtma #{oid} allaqachon qabul qilingan. Kuryerlarga yuborilgan.")
        return
    if action == "reject" and order.get("status") in ("rejected", "to_courier", "taken", "done"):
        await q.answer("Bu buyurtma allaqachon ko'rib chiqilgan")
        await _edit_q(q, f"Buyurtma #{oid} allaqachon ko'rib chiqilgan.")
        return
    # Agar buyurtma allaqachon qabul qilingan bo'lsa - yana bir marta bosganda ham ishlasin
    if action == "reject":
        order["status"] = "rejected"; save()
        try: await context.bot.send_message(chat_id=order["user_id"], text=f"❌ Buyurtma #{oid} rad etildi.")
        except: pass
        rname = DB['restaurants'][order['cafe']]['name']
        try: await context.bot.send_message(chat_id=SUPER_ADMIN, text=f"❌ Buyurtma #{oid} RAD ETILDI\nRestoran: {rname}")
        except: pass
        await _edit_q(q, "❌ Rad etildi"); return
    order["status"] = "to_courier"; save()
    r = DB["restaurants"][order["cafe"]]
    await _edit_q(q, f"✅ Buyurtma #{oid} qabul qilindi. Kuryerlarga yuborildi.")
    await context.bot.send_message(chat_id=order["user_id"], text="✅ Buyurtmangiz tasdiqlandi! Kuryer qidirilmoqda...")
    # Kanalga + online kuryerlarga
    ctext = f"🚨 YANGI BUYURTMA #{oid}!\n\n🏪 {r['name']}\n📍 {order['address']}\n👤 {order['name']} | 📞 {order['phone']}\n💰 {order['total']} so'm\n\nKim birinchi olsa - oshaniki!"
    # KANAL QOLDI - kuryer yangi buyurtmani shu kanaldan ko'radi va shu yerdan oladi.
    # Kanal postiga "MEN OLAMAN" tugmasi qaytarildi - lekin endi u qotmaydi (pastda courier_take da kanaldan bosish alohida ishlanadi).
    ckb2 = InlineKeyboardMarkup([[InlineKeyboardButton("🏃 MEN OLAMAN", callback_data=f"take_{oid}")]])
    try:
        _cm = await context.bot.send_message(chat_id=COURIER_CHANNEL, text=ctext, reply_markup=ckb2)
        order["channel_msg_id"] = _cm.message_id; save()
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
        await courier_new(q, context, "Avval telefon raqamingizni yuboring:", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
        return
    u["online"] = not u.get("online"); save()
    await q.answer("ONLINE ✅" if u["online"] else "OFFLINE 🔴")
    await show_main(update, q.from_user.id, f"Holat: {'🟢 ONLINE' if u['online'] else '🔴 OFFLINE'}")

async def courier_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    orders = [o for o in DB["orders"].values() if o["status"] == "to_courier"]
    if not orders: await courier_new(q, context, "Hozircha bo'sh buyurtma yo'q.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]])); return
    kb = []
    for o in orders:
        kb.append([InlineKeyboardButton(f"#{o['id']} | {DB['restaurants'][o['cafe']]['name']} | {o['total']} so'm | {o['address'][:30]}", callback_data=f"take_{o['id']}")])
    kb.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")])
    await courier_new(q, context, "📦 Bo'sh buyurtmalar:", reply_markup=InlineKeyboardMarkup(kb))

async def courier_take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    # TUZATILDI: oid/order ni ENG BIRINCHI olamiz - oldin ular pastda aniqlanardi, kanaldan bosganda NameError bo'lib tugma ishlamasdi. Shu edi asosiy sabab!
    oid = str(q.data.split("_")[1])
    order = DB["orders"].get(oid)
    try:
        _chat_type = q.message.chat.type if q.message and q.message.chat else "private"
    except: _chat_type = "private"
    # Guruh / super-guruh / kanal - hammasi bir xil: guruh xabarini O'CHIRMAYMIZ, faqat "OLINDI" ga yangilaymiz
    if _chat_type in ("channel", "group", "supergroup"):
        # KANALDAN OLISH - shu yerda ishlaydi! Kanal xabarini o'chirmaymiz, faqat yangilaymiz.
        if not order or order["status"] != "to_courier":
            await q.answer("Bu buyurtma allaqachon olingan!", show_alert=True); return
        if str(q.from_user.id) not in DB["users"]:
            await q.answer("Avval botda /start bosib kuryer sifatida ro'yxatdan o'ting!", show_alert=True); return
        if DB["users"][str(q.from_user.id)].get("courier_pass_hash") and not context.user_data.get("courier_logged_in"):
            await q.answer("⛔ Avval botga kirib login + parol bilan kiring! Keyin buyurtma oling.", show_alert=True)
            try: await context.bot.send_message(chat_id=q.from_user.id, text="⛔ Buyurtma olish uchun avval kiring:\n\nBotda /start bosing → Kuryer panelim → login + parolni yozing.")
            except: pass
            return
        order["status"] = "taken"; order["courier_id"] = q.from_user.id; order["courier_name"] = q.from_user.first_name; save()
        _u2 = DB["users"][str(q.from_user.id)]
        # 1) Kanaldagi postni "OLINDI" ga almashtiramiz - tugma yo'qoladi, boshqa kuryer bosolmaydi
        try: await context.bot.edit_message_text(chat_id=q.message.chat.id, message_id=q.message.message_id, text=f"✅ BUYURTMA #{oid} OLINDI!\n\n🚴 Kuryer: {q.from_user.first_name}\n🏪 {DB['restaurants'][order['cafe']]['name']}\n💰 {order['total']} so'm")
        except: pass
        # 2) Kuryerga SHAXSIY chatga tafsilot + YETKAZDIM tugmasini yuboramiz - keyingi ish shu yerda davom etadi
        try: await context.bot.send_message(chat_id=q.from_user.id, text=f"✅ Buyurtma #{oid} seniki! (kanaldan olding)\n\n📍 Manzil: {order['address']}\n📞 Mijoz: {order['phone']}\n💰 {order['total']} so'm\n\nYetkazib bo'lgach pastni bos:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ YETKAZDIM", callback_data=f"done_{oid}")]]))
        except: pass
        # 3) Mijoz + restoranga xabar
        try: await context.bot.send_message(chat_id=order["user_id"], text=f"🚴 Kuryer {_u2.get('name', q.from_user.first_name)} yo'lga chiqdi! Buyurtma #{oid} yo'lda.")
        except: pass
        try: await context.bot.send_message(chat_id=DB["restaurants"][order["cafe"]]["admin"], text=f"🚴 Kuryer {_u2.get('name', q.from_user.first_name)} buyurtma #{oid} ni oldi (kanaldan).")
        except: pass
        await q.answer("✅ Buyurtma seniki! Botga kir - tafsilot shaxsiy chatda.", show_alert=True)
        return
    oid = str(q.data.split("_")[1])
    order = DB["orders"].get(oid)
    if not order or order["status"] != "to_courier":
        await q.answer("Bu buyurtma allaqachon olingan!", show_alert=True); return
    # TUZATILDI: foydalanuvchi DB da bo'lmasa - KeyError bilan yiqilmasin
    if str(q.from_user.id) not in DB["users"]:
        await q.answer("Avval botda /start bosib kuryer sifatida ro'yxatdan o'ting!", show_alert=True); return
    # LOGIN/PAROL: paroli bor, lekin hali kirmagan kuryer buyurtma ololmaydi - birovning nomidan olib ketmasin
    _u_take = DB["users"][str(q.from_user.id)]
    if _u_take.get("courier_pass_hash") and not context.user_data.get("courier_logged_in"):
        await q.answer("⛔ Avval botga kirib login + parol bilan kiring! Keyin buyurtma oling.", show_alert=True)
        try: await context.bot.send_message(chat_id=q.from_user.id, text="⛔ Buyurtma olish uchun avval kiring:\n\nBotda /start bosing → Kuryer panelim → login + parolni yozing.")
        except: pass
        return
    order["status"] = "taken"; order["courier_id"] = q.from_user.id; order["courier_name"] = q.from_user.first_name; save()
    # Kanaldagi e'lonni "OLINDI" deb yangilaymiz - boshqa kuryerlar bosib qotib qolmasin
    _ch_mid = order.get("channel_msg_id")
    if _ch_mid:
        try: await context.bot.edit_message_text(chat_id=COURIER_CHANNEL, message_id=_ch_mid, text=f"✅ BUYURTMA #{oid} OLINDI!\n\n🚴 Kuryer: {q.from_user.first_name}\n\nYangi buyurtma kelsa shu yerda chiqadi.")
        except: pass
    u = DB["users"][str(q.from_user.id)]
    await courier_new(q, context, f"✅ Buyurtma #{oid} seniki!\n\n📍 Manzil: {order['address']}\n📞 Mijoz: {order['phone']}\n💰 {order['total']} so'm\n\nYetkazib bo'lgach pastni bos:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ YETKAZDIM", callback_data=f"done_{oid}")]]))
    await context.bot.send_message(chat_id=order["user_id"], text=f"🚴 Kuryer {u['name']} yo'lga chiqdi! Buyurtma #{oid} yo'lda.")
    # Restoranga ham xabar
    await context.bot.send_message(chat_id=DB["restaurants"][order["cafe"]]["admin"], text=f"🚴 Kuryer {u['name']} buyurtma #{oid} ni oldi.")

async def courier_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    oid = str(q.data.split("_")[1]); order = DB["orders"].get(oid)
    if not order: return
    order["status"] = "done"; save()
    uid = str(q.from_user.id)
    if uid not in DB["users"]: DB["users"][uid] = {"name": q.from_user.first_name, "role": "courier", "balance": 0, "delivered": 0}
    DB["users"][uid]["delivered"] = DB["users"][uid].get("delivered", 0) + 1; DB["users"][uid]["balance"] = DB["users"][uid].get("balance", 0) + 15000; save()
    # TUZATILDI: Yetkazdim dan keyin PANEL QAYTADI - oldin faqat matn kelardi, kuryer yana /start bosishga majbur bo'lardi
    _u_done = DB["users"].get(uid, {})
    _status_done = "🟢 ONLINE" if _u_done.get("online") else "🔴 OFFLINE"
    await courier_new(q, context, f"✅ Buyurtma #{oid} yetkazildi! +15000 so'm hisobingga qo'shildi.\n\n💰 Balans: {_u_done.get('balance',0):,} so'm\n✅ Yetkazgan: {_u_done.get('delivered',0)} ta\nHolat: {_status_done}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚴 Mening kuryer panelim", callback_data="courier_panel")],
            [InlineKeyboardButton("📦 Bo'sh buyurtmalar", callback_data="courier_list")],
            [InlineKeyboardButton("💰 Mening hisobim", callback_data="courier_balance_new")],
            [InlineKeyboardButton("🟢 ONLINE / 🔴 OFFLINE", callback_data="courier_toggle")],
        ]), parse_mode=None)
    await context.bot.send_message(chat_id=order["user_id"], text=f"✅ Buyurtmangiz #{oid} yetkazildi! Yoqimli ishtaha 😋\n\nKuryerni baholang:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⭐️⭐️⭐️⭐️⭐️", callback_data=f"rate_5_{oid}"), InlineKeyboardButton("⭐️⭐️⭐️", callback_data=f"rate_3_{oid}")]]))
    await context.bot.send_message(chat_id=SUPER_ADMIN, text=f"✅ #{oid} yetkazildi. Kuryer: {DB['users'][uid]['name']}")

async def on_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    try:
        parts = str(q.data).split("_")
        stars = int(parts[1]); oid = parts[2]
        order = DB["orders"].get(oid)
        if not order:
            # kalit int bo'lsa ham tekshiramiz
            order = DB["orders"].get(int(oid)) if oid.isdigit() else None
        if not order:
            await q.edit_message_text(f"Buyurtma topilmadi. oid={oid}")
            return
        courier_name = order.get("courier_name") or order.get("courier") or "Kuryer"
        if "ratings" not in DB: DB["ratings"] = []
        DB["ratings"].append({"order_id": oid, "courier": str(courier_name), "stars": stars, "user": q.from_user.first_name})
        save()
        await q.edit_message_text(f"Rahmat! Bahoyingiz saqlandi: {'⭐'*stars}\n✅ #{oid} yetkazildi. Kuryer: {courier_name}")
    except Exception as e:
        print("RATE ERROR:", e)
        await q.edit_message_text(f"Xato bo'ldi: {e}")
async def reyting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ratings = DB.get("ratings", [])
    if not ratings:
        await update.message.reply_text("Hali baho yo'q.")
        return
    text = "📊 Barcha baholar:\n\n"
    for r in ratings[-20:]:
        text += f"#{r['order_id']} — {r['courier']} — {'⭐'*r['stars']} — {r['user']}\n"
    avg = sum(r['stars'] for r in ratings) / len(ratings)
    text += f"\nO'rtacha: {avg:.1f} ⭐ | Jami: {len(ratings)} ta"
    await update.message.reply_text(text)
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
        if not oid_list: await courier_new(q, context, "Hozircha olingan buyurtmang yo'q.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]])); return
        o = oid_list[0]; await courier_new(q, context, f"🚴 Buyurtma #{o['id']}\n📍 {o['address']}\n📞 {o['phone']}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ YETKAZDIM", callback_data=f"done_{o['id']}")]]))
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
        await rest_menu_manage(update, context)


import hashlib as _hashlib
def courier_pass_hash(pw):
    return _hashlib.sha256(str(pw).encode()).hexdigest()[:32]

import asyncio
async def on_location(update, context):
    if not update.message.location:
        return
    loc = update.message.location
    object.__setattr__(update.message, "text", f"📍 Lokatsiya: https://maps.google.com/?q={loc.latitude},{loc.longitude}")
    await on_text(update, context)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reyting", reyting))
    app.add_handler(CallbackQueryHandler(set_role, pattern="^setrole_"))
    app.add_handler(CallbackQueryHandler(change_role, pattern="^change_role$"))
    app.add_handler(CallbackQueryHandler(client_order, pattern="^client_order$"))
    app.add_handler(CallbackQueryHandler(register_rest, pattern="^register_rest$"))
    app.add_handler(CallbackQueryHandler(cafe_menu, pattern="^cafe_"))
    app.add_handler(CallbackQueryHandler(rest_panel, pattern="^rest_panel$"))
    app.add_handler(CallbackQueryHandler(rest_menu_manage, pattern="^rest_menu$"))
    app.add_handler(CallbackQueryHandler(rest_price_list, pattern="^rest_price_list$"))
    app.add_handler(CallbackQueryHandler(rest_price_ask, pattern="^rest_price_"))
    app.add_handler(CallbackQueryHandler(rest_toggle_item, pattern="^rest_toggle_"))
    app.add_handler(CallbackQueryHandler(rest_add_ask, pattern="^rest_add$"))
    app.add_handler(CallbackQueryHandler(rest_delivery_ask, pattern="^rest_delivery$"))
    app.add_handler(CallbackQueryHandler(rest_open_toggle, pattern="^rest_open$"))
    app.add_handler(CallbackQueryHandler(rest_stats_new, pattern="^rest_stats_new$"))
    app.add_handler(CallbackQueryHandler(rest_card_ask, pattern="^rest_card$"))
    app.add_handler(CallbackQueryHandler(add_item, pattern="^add_"))
    app.add_handler(CallbackQueryHandler(confirm_cart, pattern="^confirm_cart$"))
    app.add_handler(CallbackQueryHandler(pay_select, pattern="^pay_"))
    async def _sold_out_noop(update, context):
        q = update.callback_query; await q.answer("❌ Bu taom hozircha tugagan", show_alert=True)
    app.add_handler(CallbackQueryHandler(_sold_out_noop, pattern="^sold_out_noop$"))
    app.add_handler(CallbackQueryHandler(admin_action, pattern="^(accept|reject)_"))
    app.add_handler(CallbackQueryHandler(courier_toggle, pattern="^courier_toggle$"))
    app.add_handler(CallbackQueryHandler(register_courier, pattern="^register_courier$"))
    app.add_handler(CallbackQueryHandler(register_courier_transport, pattern="^courier_tr_"))
    app.add_handler(CallbackQueryHandler(courier_panel, pattern="^courier_panel$"))
    app.add_handler(CallbackQueryHandler(courier_balance_new, pattern="^courier_balance_new$"))
    app.add_handler(CallbackQueryHandler(courier_withdraw, pattern="^courier_withdraw$"))
    app.add_handler(CallbackQueryHandler(send_phone_btn_handler, pattern="^send_phone_btn$"))
    app.add_handler(CallbackQueryHandler(courier_withdraw_approve, pattern="^wdok_"))
    app.add_handler(CallbackQueryHandler(courier_withdraw_reject, pattern="^wdno_"))
    app.add_handler(CallbackQueryHandler(courier_edit_ask, pattern="^courier_edit$"))
    app.add_handler(CallbackQueryHandler(courier_list, pattern="^courier_list$"))
    app.add_handler(CallbackQueryHandler(courier_take, pattern="^take_"))
    app.add_handler(CallbackQueryHandler(courier_done, pattern="^done_"))
    app.add_handler(CallbackQueryHandler(on_rate, pattern="^rate_"))
    app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(generic_back, pattern="^(back_main|client_my|courier_my|courier_balance|admin_orders|rest_orders|admin_couriers|admin_users|admin_rests|rest_menu|rest_stats)$"))
    app.add_handler(MessageHandler(filters.CONTACT, on_contact))
    app.add_handler(MessageHandler(filters.PHOTO, on_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(filters.LOCATION, on_location))
    print("Yandex-style bot ishga tushdi...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    # Botni to'xtamasdan ushlab turamiz
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

