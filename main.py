import asyncio
import logging
import threading
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from flask import Flask

# Твої дані
TOKEN = "8917600620:AAGme0dUQuImt9qRg_g0aCys61mcco1NwPk"
ADMIN_ID = 6836683150
CARD_NUMBER = "4874070024523381"

# Налаштування логування
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
router = Router()


# --- СТАНИ (FSM) ---
class BuyStarsStates(StatesGroup):
  waiting_for_payment_proof = State()


class WithdrawStates(StatesGroup):
  waiting_for_wallet = State()


class RefTaskStates(StatesGroup):
  waiting_for_ref_proof = State()


# --- ГОЛОВНЕ МЕНЮ ---
def get_main_keyboard():
  builder = ReplyKeyboardBuilder()
  builder.button(text="⭐ Купити зірки")
  builder.button(text="👤 Профіль")
  builder.button(text="🤝 Запросити друга")
  builder.adjust(2, 1)
  return builder.as_markup(resize_keyboard=True)


# Команда /start
@router.message(CommandStart())
async def cmd_start(message: Message):
  await message.answer(
      "👋 Вітаю у нашому магазині Telegram Stars!\n\nОбери потрібну кнопку в"
      " меню нижче:",
      reply_markup=get_main_keyboard(),
  )


# --- 1. КУПІВЛЯ ЗІРОК ТА ОПЛАТА НА КАРТУ ---
@router.message(F.text == "⭐ Купити зірки")
async def catalog_stars(message: Message):
  builder = InlineKeyboardBuilder()
  builder.button(text="50 ⭐ — 220 грн", callback_data="buy_50")
  builder.button(text="100 ⭐ — 430 грн", callback_data="buy_100")
  builder.button(text="250 ⭐ — 1050 грн", callback_data="buy_250")
  builder.button(text="500 ⭐ — 2050 грн", callback_data="buy_500")
  builder.adjust(2)

  await message.answer(
      "📦 <b>Вибери пакет зірок для покупки:</b>\n\n<i>Після вибору ти"
      " отримаєш реквізити картки для оплати.</i>",
      reply_markup=builder.as_markup(),
  )


@router.callback_query(F.data.startswith("buy_"))
async def process_buy_package(callback: CallbackQuery, state: FSMContext):
  amount_stars = callback.data.split("_")[1]

  prices = {"50": "220 грн", "100": "430 грн", "250": "1050 грн", "500": "2050 грн"}
  price_uah = prices.get(amount_stars, "220 грн")

  await state.update_data(stars=amount_stars, price=price_uah)

  text = (
      f"💳 <b>Оплата пакету: {amount_stars} ⭐</b>\n"
      f"💰 Сума до сплати: <b>{price_uah}</b>\n\n"
      f"Здійсніть переказ на картку:\n"
      f"<code>{CARD_NUMBER}</code>\n\n"
      f"⚠️ <i>Обов'язково після оплати надішли скріншот (квитанцію) у цей чат"
      f" кнопкою нижче!</i>"
  )

  builder = InlineKeyboardBuilder()
  builder.button(text="❌ Скасувати", callback_data="cancel_buy")

  await callback.message.edit_text(text, reply_markup=builder.as_markup())
  await state.set_state(BuyStarsStates.waiting_for_payment_proof)
  await callback.answer()


@router.callback_query(F.data == "cancel_buy")
async def cancel_buy(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  await callback.message.edit_text("❌ Покупку скасовано.")
  await callback.answer()


@router.message(BuyStarsStates.waiting_for_payment_proof, F.photo)
async def receive_payment_proof(message: Message, state: FSMContext):
  data = await state.get_data()
  stars = data.get("stars")
  price = data.get("price")

  photo_file_id = message.photo[-1].file_id
  user_id = message.from_user.id
  username = message.from_user.username or "немає"

  builder = InlineKeyboardBuilder()
  builder.button(
      text="✅ Підтвердити і видати зірки",
      callback_data=f"pay_accept_{user_id}_{stars}",
  )
  builder.button(text="❌ Відхилити", callback_data=f"pay_decline_{user_id}")
  builder.adjust(1)

  await message.bot.send_photo(
      ADMIN_ID,
      photo=photo_file_id,
      caption=(

  
