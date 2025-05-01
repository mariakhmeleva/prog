import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from dotenv import load_dotenv
import asyncio


load_dotenv()
API_TOKEN = os.getenv("API_TOKEN") #получаем токен из .env


bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


currency_data = {} #словарь валют

class SaveCurrency(StatesGroup):    #класс для сохранения валюты
    waiting_for_name = State()          
    waiting_for_rate = State()

@dp.message(F.text == "/save_currency") #обработчик команды /save_currency
async def start_save_currency(message: Message, state: FSMContext): #функция обработки запроса команды пользователя
    await message.answer("Введите название валюты:")
    await state.set_state(SaveCurrency.waiting_for_name)


@dp.message(SaveCurrency.waiting_for_name) # 
async def get_currency_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.upper())
    await message.answer("Введите курс к рублю:")
    await state.set_state(SaveCurrency.waiting_for_rate)

@dp.message(SaveCurrency.waiting_for_rate)
async def get_currency_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text.replace(",", "."))
        data = await state.get_data()
        currency_data[data["name"]] = rate
        await message.answer(f"Сохранено: 1 {data['name']} = {rate} RUB")
        await state.clear()
    except ValueError:
        await message.answer("Введите число, например: 89.5")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())