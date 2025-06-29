from aiogram import Bot, Dispatcher, types, executor
from fpdf import FPDF
import os

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@urunovs_blog")
INSTAGRAM_LINK = "https://www.instagram.com/urunov_official_?igsh=dmx4cm13aHFzemZn"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

counter_file = "counter.txt"
issued_users = set()

def load_counter():
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            return int(f.read())
    else:
        return 1

def save_counter(counter):
    with open(counter_file, "w") as f:
        f.write(str(counter))

class CustomPDF(FPDF):
    def header(self):
        pass

async def check_channel_member(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub"))
    await message.answer(
        "🎯 <b>Assalomu alaykum, Liderlik sari yo‘lni tanlagan aziz do‘st!</b>\n\n"
        "@urunovs_blog tomonidan yaratilgan bot sizni Shoxijahon Urunovning <b>“Liderlik sari”</b> loyihasiga taklif etadi.\n\n"
        "🚀 <b>Bu loyiha orqali faqat faol ishtirokchilarga ochiladigan ajoyib imkoniyatlar, tanlovlar va xalqaro maydon sari yo‘llar kutmoqda!</b>\n\n"
        "💡 <b>Kichik shartimiz:</b> Quyidagi sahifalarimizga obuna bo‘ling:\n"
        f"👉 Telegram: <a href='https://t.me/urunovs_blog'>@urunovs_blog</a>\n"
        f"👉 Instagram: <a href='{INSTAGRAM_LINK}'>urunov_official_</a>\n\n"
        "✅ <b>Obunani bajargach, pastdagi tugmani bosing yoki Ism Familiyangizni yuboring.</b>\n"
        "Namuna: Shoxijahon Urunov",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == 'check_sub')
async def process_check_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    is_member = await check_channel_member(user_id)
    if is_member:
        await bot.answer_callback_query(callback_query.id, "✅ Obuna muvaffaqiyatli tasdiqlandi. Endi Ism Familiyangizni yuboring!")
    else:
        await bot.answer_callback_query(callback_query.id, "❗ Hali obuna bo‘lmadingiz. Iltimos, @urunovs_blog kanaliga obuna bo‘ling.")

@dp.message_handler()
async def name_handler(message: types.Message):
    user_id = message.from_user.id

    is_member = await check_channel_member(user_id)
    if not is_member:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub"))
        await message.answer(
            "❗ <b>Kichik shartimizni bajaring:</b> <a href='https://t.me/urunovs_blog'>@urunovs_blog</a> kanaliga obuna bo‘ling va pastdagi tugma orqali tekshiring.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    if user_id in issued_users:
        await message.answer("✅ Sizga allaqachon guvohnoma berildi. Bizni kuzatib boring — ko‘plab nashrlar, tanlovlar va imkoniyatlar kutmoqda!")
        return

    name = message.text.strip()
    if len(name.split()) < 2:
        await message.answer("❗ Iltimos, to‘liq Ism Familiyangizni yuboring. Namuna: Shoxijahon Urunov")
        return

    await message.answer("⏳ Sertifikatingiz tayyorlanmoqda...")

    counter = load_counter()

    pdf = CustomPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.image('sertifikat_shablon.png', x=0, y=0, w=297, h=210)

    pdf.set_text_color(0, 0, 200)
    pdf.set_font("Arial", 'B', 36)
    pdf.set_xy(0, 110)
    pdf.cell(297, 10, txt=name, align='C')

    pdf.set_text_color(0, 0, 200)
    pdf.set_font("Arial", size=12)
    pdf.set_xy(200, 200)
    pdf.cell(90, 10, f"SERTIFIKAT NOMERI: {counter}", align='R')

    file_name = f"sertifikat_{user_id}.pdf"
    pdf.output(file_name)

    await message.answer_document(
        types.InputFile(file_name),
        caption=(
            "🎉 <b>Tabriklaymiz! Siz “Liderlik sari” loyihamizga muvaffaqiyatli qo‘shildingiz.</b>\n"
            "Endi eng qiziqarli qism boshlanadi — faqat faol ishtirokchilarga ochiladigan imkoniyatlar, tanlovlar, nashrlar va xalqaro maydon sari yo‘llar kutmoqda!\n"
            "🚀 <b>Bizni doimiy kuzatib boring, har bir yangilik sizning muvaffaqiyatingiz sari qadam bo‘ladi.</b>\n"
            "<b>Esda tuting: O‘zgarish — o‘z qo‘lingizda!</b>"
        ),
        parse_mode="HTML"
    )

    issued_users.add(user_id)
    counter += 1
    save_counter(counter)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
