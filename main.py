import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Твої персональні дані
TOKEN = "8917600620:AAGme0dUQuImt9qRg_g0aCys61mcco1NwPk"
ADMIN_ID = 6836683150  
ADMIN_USERNAME = "Primeinfo0"

dp = Dispatcher()
bot = Bot(token=TOKEN)

def get_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Купити Telegram Stars", callback_data="buy_stars")],
            [InlineKeyboardButton(text="📋 Завдання за зірки", callback_data="tasks")],
            [InlineKeyboardButton(text="👤 Профіль / Баланс", callback_data="profile")],
            [InlineKeyboardButton(text="💬 Підтримка", url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
    )

def get_stars_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ 50 зірок — 45 грн", callback_data="stars_50")],
            [InlineKeyboardButton(text="⭐ 100 зірок — 85 грн", callback_data="stars_100")],
            [InlineKeyboardButton(text="⭐ 250 зірок — 200 грн", callback_data="stars_250")],
            [InlineKeyboardButton(text="⭐ 500 зірок — 390 грн", callback_data="stars_500")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ]
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🚀 **Вітаємо у нашому сервісі!**\n\nОберіть потрібний розділ нижче:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

# Адмін-команда для відповіді покупцю: /reply ID текст
@dp.message(Command("reply"))
async def admin_reply(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("⚠️ Використання: `/reply [ID_користувача] [текст]`", parse_mode="Markdown")
        return
    
    client_id = args[1]
    reply_text = args[2]
    
    try:
        await bot.send_message(
            chat_id=int(client_id),
            text=f"💬 **Повідомлення від адміністратора (@{ADMIN_USERNAME}):**\n\n{reply_text}",
            parse_mode="Markdown"
        )
        await message.answer(f"✅ Повідомлення надіслано користувачу `{client_id}`!", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Помилка надсилання: {e}")

@dp.callback_query(F.data == "buy_stars")
async def process_buy_stars(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⭐ **Придбання Telegram Stars**\n\nВиберіть пакет зірок:",
        reply_markup=get_stars_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("stars_"))
async def process_selected_stars(callback: types.CallbackQuery):
    amount = callback.data.split("_")[1]
    prices = {"50": "45 грн", "100": "85 грн", "250": "200 грн", "500": "390 грн"}
    price = prices.get(amount, "0 грн")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Сплачено / Перевірити", callback_data=f"pay_{amount}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="buy_stars")]
        ]
    )
    await callback.message.edit_text(
        f"💳 **Оплата замовлення**\n\n📦 Пакет: **{amount} зірок**\n💵 До сплати: **{price}**\n\nПісля оплати натисніть кнопку нижче:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def process_check_payment(callback: types.CallbackQuery):
    amount = callback.data.split("_")[1]
    user = callback.from_user
    
    await callback.answer("⏳ Запит на перевірку відправлено адміністратору!", show_alert=True)
    await callback.message.edit_text(
        "⏳ **Запит на перевірку прийнято!**\n\nАдміністратор скоро перевірить оплату та нарахує зірки.",
        parse_mode="Markdown"
    )
    
    try:
        admin_text = (
            "🚨 **НОВЕ ЗАМОВЛЕННЯ!**\n\n"
            f"👤 Клієнт: @{user.username or 'немає'} (ID: `{user.id}`)\n"
            f"👤 Ім'я: {user.first_name}\n"
            f"📦 Замовлено зірок: **{amount} ⭐**\n\n"
            f"✍️ **Відповідь клієнту через команду:**\n"
            f"`/reply {user.id} Привіт, твої зірки готові!`"
        )
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Помилка надсилання адміну: {e}")

@dp.callback_query(F.data == "tasks")
async def process_tasks(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]])
    await callback.message.edit_text("📋 **Доступні завдання**\n\n1. Підписка на канал (+5 зірок)", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "profile")
async def process_profile(callback: types.CallbackQuery):
    user = callback.from_user
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]])
    await callback.message.edit_text(f"👤 **Профіль**\n\nID: `{user.id}`\n⭐ Баланс: **0 ⭐**", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def process_back(callback: types.CallbackQuery):
    await callback.message.edit_text("🚀 **Головне меню:**", reply_markup=get_main_menu(), parse_mode="Markdown")
    await callback.answer()

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот успішно запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
