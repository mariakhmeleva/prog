import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")  


bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

main_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="/convert")],
    [KeyboardButton(text="/get_currencies")],
    [KeyboardButton(text="/manage_currency")],
])


@dp.message(F.text == "/start")
async def start_cmd(msg: Message):
    await msg.answer("Привет! Выберите действие из меню:", reply_markup=main_menu)


@dp.message(F.text == "/get_currencies")
async def get_currencies(msg: Message):
    res = requests.get("http://localhost:5002/currencies")
    if res.status_code != 200:
        await msg.answer("Ошибка при получении валют.")
        return
    currencies = res.json()
    if not currencies:
        await msg.answer("Валют пока нет.")
        return
    text = "\n".join([f"{c['currency_name']}: {c['rate']}₽" for c in currencies])
    await msg.answer(text)

# Для convert
class ConvertState(StatesGroup):
    waiting_currency = State()
    waiting_amount = State()

@dp.message(F.text == "/convert")
async def convert_start(msg: Message, state: FSMContext):
    await msg.answer("Введите название валюты:")
    await state.set_state(ConvertState.waiting_currency)

@dp.message(ConvertState.waiting_currency)
async def convert_currency(msg: Message, state: FSMContext):
    await state.update_data(currency=msg.text)
    await msg.answer("Введите сумму:")
    await state.set_state(ConvertState.waiting_amount)

@dp.message(ConvertState.waiting_amount)
async def convert_amount(msg: Message, state: FSMContext):
    try:
        amount = float(msg.text)
    except ValueError:
        await msg.answer("Введите корректную сумму.")
        return
    data = await state.get_data()
    currency = data['currency']
    res = requests.get(f"http://localhost:5002/convert?currency_name={currency}&amount={amount}")
    if res.status_code != 200:
        await msg.answer("Ошибка: валюта не найдена.")
    else:
        converted = res.json()['converted']
        await msg.answer(f"{amount} {currency} = {converted:.2f}₽")
    await state.clear()


class ManageCurrencyState(StatesGroup):
    action = State()
    currency = State()
    rate = State()

@dp.message(F.text == "/manage_currency")
async def manage_currency_start(msg: Message, state: FSMContext):
    res = requests.get(f"http://localhost:5001/get_role/{msg.from_user.id}")
    if res.status_code != 200 or res.json().get("role") != "admin":
        await msg.answer("У вас нет доступа к этой команде.")
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Добавить валюту")],
        [KeyboardButton(text="Удалить валюту")],
        [KeyboardButton(text="Изменить курс валюты")]
    ])
    await msg.answer("Выберите действие:", reply_markup=kb)
    await state.set_state(ManageCurrencyState.action)

@dp.message(ManageCurrencyState.action)
async def manage_action(msg: Message, state: FSMContext):
    action = msg.text
    if action not in ["Добавить валюту", "Удалить валюту", "Изменить курс валюты"]:
        await msg.answer("Неверный выбор. Повторите.")
        return
    await state.update_data(action=action)
    await msg.answer("Введите название валюты:")
    await state.set_state(ManageCurrencyState.currency)

@dp.message(ManageCurrencyState.currency)
async def manage_currency_name(msg: Message, state: FSMContext):
    await state.update_data(currency=msg.text)
    data = await state.get_data()
    action = data['action']

    if action == "Удалить валюту":
        res = requests.post("http://localhost:5001/delete", json={"currency_name": msg.text})
        if res.status_code == 200:
            await msg.answer("Валюта успешно удалена.")
        else:
            await msg.answer("Валюта не найдена.")
        await state.clear()
    elif action in ["Добавить валюту", "Изменить курс валюты"]:
        await msg.answer("Введите курс:")
        await state.set_state(ManageCurrencyState.rate)

@dp.message(ManageCurrencyState.rate)
async def manage_currency_rate(msg: Message, state: FSMContext):
    try:
        rate = float(msg.text)
    except ValueError:
        await msg.answer("Введите число.")
        return
    data = await state.get_data()
    name = data['currency']
    action = data['action']

    if action == "Добавить валюту":
        res = requests.post("http://localhost:5001/load", json={"currency_name": name, "rate": rate})
        if res.status_code == 200:
            await msg.answer(f"Валюта {name} успешно добавлена.")
        else:
            await msg.answer("Валюта уже существует.")
    elif action == "Изменить курс валюты":
        res = requests.post("http://localhost:5001/update_currency", json={"currency_name": name, "rate": rate})
        if res.status_code == 200:
            await msg.answer(f"Курс валюты {name} обновлён.")
        else:
            await msg.answer("Валюта не найдена.")

    await state.clear()

# === Запуск ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
