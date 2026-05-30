"""
Legal Support Center — Telegram Bot
Запуск: python bot.py
Зависимости: pip install aiogram==3.x
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ───────────────────────────────────────────
# НАСТРОЙКИ
# ───────────────────────────────────────────
BOT_TOKEN = "8375788079:AAFdia486f63RHbxWHApEu5ysZDjS9vtHYM"
ADMIN_USERNAME = "LegalSuppportCenter"  # Без @
ADMIN_CHAT_ID = None                    # Заполнится автоматически при первом /start от админа

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ───────────────────────────────────────────
# СОСТОЯНИЯ (FSM)
# ───────────────────────────────────────────
class Application(StatesGroup):
    waiting_name    = State()
    waiting_phone   = State()
    waiting_problem = State()

class FreeQuestion(StatesGroup):
    waiting_question = State()

# ───────────────────────────────────────────
# КЛАВИАТУРЫ
# ───────────────────────────────────────────
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚖️ Услуги",           callback_data="services")],
        [InlineKeyboardButton(text="🎖 Военное право",     callback_data="cat_military")],
        [InlineKeyboardButton(text="📋 Подать заявку",     callback_data="apply")],
        [InlineKeyboardButton(text="❓ Задать вопрос",     callback_data="free_question")],
        [InlineKeyboardButton(text="📞 Контакты",          callback_data="contacts")],
    ])

def services_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎖 Военное право",           callback_data="cat_military")],
        [InlineKeyboardButton(text="⚖️ Уголовное право",         callback_data="cat_criminal")],
        [InlineKeyboardButton(text="🏛 Гражданские дела",         callback_data="cat_civil")],
        [InlineKeyboardButton(text="📋 Административное право",   callback_data="cat_admin")],
        [InlineKeyboardButton(text="🏢 Бизнес и регистрация",    callback_data="cat_business")],
        [InlineKeyboardButton(text="🔬 Экспертизы",              callback_data="cat_expert")],
        [InlineKeyboardButton(text="🌍 Земельные отношения",      callback_data="cat_land")],
        [InlineKeyboardButton(text="📄 Лицензирование",           callback_data="cat_license")],
        [back_btn()],
    ])

def back_btn() -> InlineKeyboardButton:
    return InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")

def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_btn()]])

def apply_or_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Подать заявку", callback_data="apply")],
        [back_btn()],
    ])

def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# ───────────────────────────────────────────
# ТЕКСТЫ КАТЕГОРИЙ
# ───────────────────────────────────────────
CATEGORIES = {
    "cat_military": {
        "title": "🎖 Военное право",
        "text": (
            "Мы — команда опытных военных юристов, которая уже помогла более <b>100 людям</b> "
            "защитить свои права.\n\n"
            "<b>Что мы делаем:</b>\n"
            "✅ Законное списание с армии (по болезни, семейным обстоятельствам и др.)\n"
            "✅ Получение выплат, страховок и компенсаций\n"
            "✅ Перевод к новому месту службы\n"
            "✅ Защита от незаконных приказов и давления командования\n"
            "✅ Обжалование дисциплинарных взысканий\n"
            "✅ Помощь при уголовном преследовании военнослужащих\n\n"
            "⚡️ Работаем быстро и конфиденциально."
        )
    },
    "cat_criminal": {
        "title": "⚖️ Уголовное право",
        "text": (
            "<b>Уголовное право:</b>\n\n"
            "✅ Защита по уголовным делам на всех стадиях\n"
            "✅ Представление интересов обвиняемых и подозреваемых\n"
            "✅ Обжалование приговоров и постановлений\n"
            "✅ Помощь потерпевшим\n"
            "✅ Прекращение уголовных дел\n"
            "✅ Досудебные соглашения о сотрудничестве"
        )
    },
    "cat_civil": {
        "title": "🏛 Гражданские дела",
        "text": (
            "<b>Гражданские дела:</b>\n\n"
            "✅ Споры по договорам (займы, аренда, подряд)\n"
            "✅ Защита прав потребителей\n"
            "✅ Наследственные споры\n"
            "✅ Семейное право (развод, алименты, раздел имущества)\n"
            "✅ Трудовые споры (незаконное увольнение, невыплата зарплаты)\n"
            "✅ Взыскание долгов"
        )
    },
    "cat_admin": {
        "title": "📋 Административное право",
        "text": (
            "<b>Административное право:</b>\n\n"
            "✅ Обжалование штрафов ГИБДД и других органов\n"
            "✅ Защита при проверках государственных органов\n"
            "✅ Обжалование решений государственных органов\n"
            "✅ Представление интересов в суде по административным делам\n"
            "✅ Лишение прав — обжалование"
        )
    },
    "cat_business": {
        "title": "🏢 Бизнес и регистрация",
        "text": (
            "<b>Бизнес и регистрация:</b>\n\n"
            "✅ Регистрация ИП, ООО, НКО\n"
            "✅ Ликвидация и реорганизация компаний\n"
            "✅ Арбитражные споры\n"
            "✅ Составление договоров и правовая экспертиза\n"
            "✅ Юридическое сопровождение бизнеса\n"
            "✅ Взыскание дебиторской задолженности"
        )
    },
    "cat_expert": {
        "title": "🔬 Экспертизы",
        "text": (
            "<b>Экспертизы:</b>\n\n"
            "✅ Проверка на полиграфе (детекторе лжи)\n"
            "✅ Экспертиза ДНК\n"
            "✅ Организация независимых экспертиз\n"
            "✅ Юридическое сопровождение результатов экспертизы в суде"
        )
    },
    "cat_land": {
        "title": "🌍 Земельные отношения",
        "text": (
            "<b>Земельные отношения:</b>\n\n"
            "✅ Оформление прав на земельные участки\n"
            "✅ Земельные споры и споры о границах\n"
            "✅ Перевод земель в другую категорию\n"
            "✅ Защита от незаконного изъятия земли\n"
            "✅ Кадастровые вопросы"
        )
    },
    "cat_license": {
        "title": "📄 Лицензирование",
        "text": (
            "<b>Лицензирование:</b>\n\n"
            "✅ Получение лицензий для любых видов деятельности\n"
            "✅ Медицинские, образовательные, охранные лицензии\n"
            "✅ Обжалование отказов в выдаче лицензий\n"
            "✅ Продление и переоформление лицензий"
        )
    },
}

# ───────────────────────────────────────────
# /START
# ───────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message):
    # Запоминаем chat_id админа
    global ADMIN_CHAT_ID
    if message.from_user.username == ADMIN_USERNAME:
        ADMIN_CHAT_ID = message.chat.id

    name = message.from_user.first_name or "друг"
    await message.answer(
        f"👋 Добро пожаловать, <b>{name}</b>!\n\n"
        "⚖️ <b>Legal Support Center</b> — команда опытных юристов.\n\n"
        "🛡 <b>Защита ваших прав — наша миссия!</b>\n\n"
        "Более 100 успешных дел. Работаем по всей стране.\n\n"
        "Выберите, что вас интересует:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

# ───────────────────────────────────────────
# ГЛАВНОЕ МЕНЮ (callback)
# ───────────────────────────────────────────
@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        "⚖️ <b>Legal Support Center</b>\n\n"
        "🛡 <b>Защита ваших прав — наша миссия!</b>\n\n"
        "Выберите раздел:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

# ───────────────────────────────────────────
# МЕНЮ УСЛУГ
# ───────────────────────────────────────────
@dp.callback_query(F.data == "services")
async def cb_services(call: CallbackQuery):
    await call.message.edit_text(
        "📂 <b>Наши услуги</b>\n\n"
        "Выберите категорию, которая вас интересует:",
        parse_mode="HTML",
        reply_markup=services_menu()
    )

# ───────────────────────────────────────────
# КАТЕГОРИИ УСЛУГ
# ───────────────────────────────────────────
@dp.callback_query(F.data.in_(CATEGORIES.keys()))
async def cb_category(call: CallbackQuery):
    cat = CATEGORIES[call.data]
    await call.message.edit_text(
        f"<b>{cat['title']}</b>\n\n{cat['text']}\n\n"
        "💬 Хотите получить консультацию по этому направлению?",
        parse_mode="HTML",
        reply_markup=apply_or_back()
    )

# ───────────────────────────────────────────
# КОНТАКТЫ
# ───────────────────────────────────────────
@dp.callback_query(F.data == "contacts")
async def cb_contacts(call: CallbackQuery):
    await call.message.edit_text(
        "📞 <b>Контакты Legal Support Center</b>\n\n"
        "📢 <b>Канал:</b> @LegalSuppportCenter_channel\n"
        "👤 <b>Оператор:</b> @LegalSuppportCenter\n\n"
        "📱 <b>Номера для связи (Max, Telegram):</b>\n"
        "+7 (949) 782-81-47\n"
        "+7 (949) 098-33-96\n\n"
        "📧 <b>Почта:</b> legalsupport.center@gmail.com\n\n"
        "🕐 Работаем <b>24/7</b> по всей стране\n"
        "Первичная консультация — <b>бесплатно</b>!",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Канал",         url="https://t.me/LegalSuppportCenter_channel")],
            [InlineKeyboardButton(text="👤 Оператор",      url="https://t.me/LegalSuppportCenter")],
            [InlineKeyboardButton(text="📋 Подать заявку", callback_data="apply")],
            [back_btn()],
        ])
    )

# ───────────────────────────────────────────
# ЗАЯВКА — СТАРТ
# ───────────────────────────────────────────
@dp.callback_query(F.data == "apply")
async def cb_apply(call: CallbackQuery, state: FSMContext):
    await state.set_state(Application.waiting_name)
    await call.message.answer(
        "📋 <b>Подача заявки</b>\n\n"
        "Шаг 1 из 3\n"
        "Введите ваше <b>имя</b>:",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )
    await call.answer()

@dp.message(Application.waiting_name)
async def apply_name(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заявка отменена.", reply_markup=main_menu())
        return
    await state.update_data(name=message.text)
    await state.set_state(Application.waiting_phone)
    await message.answer(
        "Шаг 2 из 3\n"
        "Введите ваш <b>номер телефона</b> или Telegram для связи:",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )

@dp.message(Application.waiting_phone)
async def apply_phone(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заявка отменена.", reply_markup=main_menu())
        return
    await state.update_data(phone=message.text)
    await state.set_state(Application.waiting_problem)
    await message.answer(
        "Шаг 3 из 3\n"
        "Опишите вашу <b>ситуацию или вопрос</b> кратко:",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )

@dp.message(Application.waiting_problem)
async def apply_problem(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заявка отменена.", reply_markup=main_menu())
        return

    data = await state.get_data()
    await state.clear()

    user = message.from_user
    username_str = f"@{user.username}" if user.username else "нет username"

    # Сообщение клиенту
    await message.answer(
        "✅ <b>Заявка принята!</b>\n\n"
        "Мы свяжемся с вами в ближайшее время.\n"
        "Первичная консультация — <b>бесплатно</b>.\n\n"
        "⚖️ <b>Legal Support Center</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Наш канал", url="https://t.me/LegalSuppportCenter_channel")],
            [InlineKeyboardButton(text="◀️ В главное меню", callback_data="main_menu")],
        ])
    )

    # Пересылка админу
    admin_text = (
        "🔔 <b>НОВАЯ ЗАЯВКА</b>\n\n"
        f"👤 <b>Имя:</b> {data.get('name', '—')}\n"
        f"📱 <b>Контакт:</b> {data.get('phone', '—')}\n"
        f"💬 <b>Проблема:</b>\n{message.text}\n\n"
        f"🔗 <b>Telegram:</b> {username_str}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>"
    )

    # Отправка по username если нет ADMIN_CHAT_ID
    target = ADMIN_CHAT_ID or f"@{ADMIN_USERNAME}"
    try:
        await bot.send_message(target, admin_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Не удалось отправить заявку админу: {e}")

# ───────────────────────────────────────────
# БЕСПЛАТНЫЙ ВОПРОС
# ───────────────────────────────────────────
@dp.callback_query(F.data == "free_question")
async def cb_free_question(call: CallbackQuery, state: FSMContext):
    await state.set_state(FreeQuestion.waiting_question)
    await call.message.answer(
        "❓ <b>Задайте ваш вопрос</b>\n\n"
        "Напишите вопрос — юрист ответит вам лично:",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )
    await call.answer()

@dp.message(FreeQuestion.waiting_question)
async def receive_question(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu())
        return

    await state.clear()
    user = message.from_user
    username_str = f"@{user.username}" if user.username else "нет username"

    await message.answer(
        "✅ <b>Вопрос отправлен!</b>\n\n"
        "Юрист ответит вам в ближайшее время.\n\n"
        "⚖️ <b>Legal Support Center</b>",
        parse_mode="HTML",
        reply_markup=back_keyboard()
    )

    admin_text = (
        "❓ <b>НОВЫЙ ВОПРОС</b>\n\n"
        f"💬 {message.text}\n\n"
        f"👤 {user.first_name or ''} {user.last_name or ''}\n"
        f"🔗 {username_str}\n"
        f"🆔 <code>{user.id}</code>"
    )
    target = ADMIN_CHAT_ID or f"@{ADMIN_USERNAME}"
    try:
        await bot.send_message(target, admin_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Не удалось отправить вопрос админу: {e}")

# ───────────────────────────────────────────
# КОМАНДА /admin — получить свой chat_id
# ───────────────────────────────────────────
@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    global ADMIN_CHAT_ID
    if message.from_user.username == ADMIN_USERNAME:
        ADMIN_CHAT_ID = message.chat.id
        await message.answer(
            f"✅ Ваш Chat ID сохранён: <code>{ADMIN_CHAT_ID}</code>\n"
            "Теперь заявки будут приходить сюда.",
            parse_mode="HTML"
        )
    else:
        await message.answer("⛔️ Нет доступа.")

# ───────────────────────────────────────────
# ЗАПУСК
# ───────────────────────────────────────────
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
