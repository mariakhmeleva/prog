import os
import psycopg2
import requests
from datetime import date
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import asyncio

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "postgres",
    "database": "RGZ"
}

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Определение состояний
class RegistrationState(StatesGroup):
    waiting_for_name = State()

class AddOperationState(StatesGroup):
    choosing_type = State()
    entering_amount = State()
    entering_date = State()

class CurrencyState(StatesGroup):
    choosing_currency = State()

# Клавиатуры
operation_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ДОХОД"), KeyboardButton(text="РАСХОД")]
    ],
    resize_keyboard=True
)

currency_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="RUB"), KeyboardButton(text="USD"), KeyboardButton(text="EUR")]
    ],
    resize_keyboard=True
)

def get_db():
    return psycopg2.connect(**DB_CONFIG)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать в финансовый бот!\n"
        "Доступные команды:\n"
        "/reg - Регистрация\n"
        "/add_operation - Добавить операцию\n"
        "/operations - Просмотр операций\n"
        "/lk - Личный кабинет"
    )

@dp.message(Command("reg"))
async def register_user(message: types.Message, state: FSMContext):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if cursor.fetchone():
        await message.answer("Вы уже зарегистрированы!")
        return
    
    await message.answer("Введите ваш логин:")
    await state.set_state(RegistrationState.waiting_for_name)

@dp.message(RegistrationState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (chat_id, name) VALUES (%s, %s)",
        (message.chat.id, message.text)
    )
    conn.commit()
    await message.answer("Регистрация завершена!")
    await state.clear()

@dp.message(Command("add_operation"))
async def add_operation_start(message: types.Message, state: FSMContext):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if not cursor.fetchone():
        await message.answer("Сначала зарегистрируйтесь с помощью /reg")
        return
    
    await message.answer("Выберите тип операции:", reply_markup=operation_type_kb)
    await state.set_state(AddOperationState.choosing_type)

@dp.message(AddOperationState.choosing_type)
async def process_type(message: types.Message, state: FSMContext):
    if message.text not in ["ДОХОД", "РАСХОД"]:
        await message.answer("Пожалуйста, выберите тип операции из кнопок")
        return
    
    await state.update_data(operation_type=message.text)
    await message.answer("Введите сумму операции в рублях:")
    await state.set_state(AddOperationState.entering_amount)

@dp.message(AddOperationState.entering_amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму (положительное число)")
        return
    
    await state.update_data(amount=amount)
    await message.answer("Введите дату операции в формате ГГГГ-ММ-ДД:")
    await state.set_state(AddOperationState.entering_date)

@dp.message(AddOperationState.entering_date)
async def process_date(message: types.Message, state: FSMContext):
    try:
        op_date = date.fromisoformat(message.text)
    except ValueError:
        await message.answer("Неверный формат даты. Используйте ГГГГ-ММ-ДД")
        return
    
    data = await state.get_data()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO operations (date, amount, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
        (op_date, data['amount'], message.chat.id, data['operation_type'])
    )
    conn.commit()
    await message.answer("Операция успешно добавлена!")
    await state.clear()

@dp.message(Command("operations"))
async def show_operations(message: types.Message, state: FSMContext):
    await message.answer("Выберите валюту для отображения:", reply_markup=currency_kb)
    await state.set_state(CurrencyState.choosing_currency)

@dp.message(CurrencyState.choosing_currency)
async def process_currency(message: types.Message, state: FSMContext):
    currency = message.text
    rate = 1.0
    
    if currency not in ["RUB", "USD", "EUR"]:
        await message.answer("Пожалуйста, выберите валюту из предложенных")
        return
    
    if currency != "RUB":
        try:
            response = requests.get(f'http://localhost:5000/rate?currency={currency}')
            if response.status_code == 200:
                rate = response.json()['rate']
            else:
                await message.answer("Ошибка получения курса валют")
                return
        except Exception as e:
            await message.answer("Ошибка подключения к сервису курсов")
            return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM operations WHERE chat_id = %s ORDER BY date DESC",
        (message.chat.id,)
    )
    operations = cursor.fetchall()
    
    response = ["Ваши операции:"]
    total = 0.0
    for op in operations:
        converted = float(op[2]) / rate
        response.append(
            f"{op[1]}: {op[4]} - {converted:.2f} {currency}"
        )
        total += converted
    
    response.append(f"\nИтого: {total:.2f} {currency}")
    await message.answer("\n".join(response))
    await state.clear()

@dp.message(Command("lk"))
async def show_profile(message: types.Message):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT name, registration_date FROM users WHERE chat_id = %s",
        (message.chat.id,)
    )
    user = cursor.fetchone()
    
    if not user:
        await message.answer("Сначала зарегистрируйтесь с помощью /reg")
        return
    
    cursor.execute(
        "SELECT COUNT(*) FROM operations WHERE chat_id = %s",
        (message.chat.id,)
    )
    operations_count = cursor.fetchone()[0]
    
    response = (
        f"👤 Логин: {user[0]}\n"
        f"📅 Дата регистрации: {user[1]}\n"
        f"💼 Всего операций: {operations_count}"
    )
    await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())