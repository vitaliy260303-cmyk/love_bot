import asyncio, os, random
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from groq import AsyncGroq
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import *

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
scheduler = AsyncIOScheduler()

def days_text():
    d = datetime.now() - MEETING_DATE
    return f"{d.days} дней, {d.seconds // 3600} ч, {(d.seconds % 3600) // 60} мин"

def kb():
    b = InlineKeyboardBuilder()
    b.button(text="💌 Комплимент", callback_data="compliment")
    b.button(text="💭 Вопрос дня", callback_data="question")
    b.button(text="🎁 Сюрприз", callback_data="surprise")
    b.button(text="⏳ Сколько вместе", callback_data="days")
    return b.adjust(2).as_markup()

@dp.message(Command("start"))
async def start(m: Message):
    if m.from_user.id not in ALLOWED_IDS:
        return await m.answer("Этот бот создан для одной особенной девушки. 💕")
        
    txt = f"Привет, {GIRLFRIEND_NAME} 💕\n\nЭтот бот создан для тебя — {YOUR_NAME} старался ✨\n\nМы вместе уже: <b>{days_text()}</b>"
    await m.answer(txt, reply_markup=kb(), parse_mode="HTML")

@dp.callback_query(F.data == "days")
async def days(cb: CallbackQuery):
    await cb.message.answer(f"⏳ Мы вместе уже <b>{days_text()}</b> 💖", parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "compliment")
async def compliment(cb: CallbackQuery):
    await cb.answer("Пишу... ✍️")
    try:
        r = await groq_client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=[
                {"role": "system", "content": f"Напиши короткое романтичное послание для {GIRLFRIEND_NAME} от {YOUR_NAME}."}, 
                {"role": "user", "content": "Новое"}
            ]
        )
        await cb.message.answer(f"💌 {r.choices[0].message.content.strip()}")
    except Exception as e:
        print(e)
        await cb.message.answer("Ой, задумался... 💕")

@dp.callback_query(F.data == "question")
async def question(cb: CallbackQuery):
    q = random.choice([
        "Какой твой любимый момент с нами?", 
        "Что бы ты хотела сделать вместе на выходных?", 
        "Каким ты видишь наш идеальный день?", 
        "Что заставляет тебя улыбаться?", 
        "О каком путешествии ты мечтаешь?", 
        "Какая песня напоминает тебе о нас?"
    ])
    await cb.message.answer(f"💭 <b>Вопрос дня:</b>\n\n{q}", parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "surprise")
async def surprise(cb: CallbackQuery):
    await cb.answer("🎁")
    if random.random() < 0.4:
        await cb.message.answer(f"💙 <b>Личное для тебя:</b>\n\n{SECRET_MESSAGE}", parse_mode="HTML")
    else:
        await cb.message.answer(random.choice([
            "🌟 Ты — лучшее, что случилось со мной.", 
            f"💖 {YOUR_NAME} думает о тебе.", 
            "🌹 Ты делаешь каждый день ярче.", 
            "✨ Ты — моё любимое доброе утро.", 
            "💫 Я люблю тебя всё больше.", 
            "🦋 Рядом с тобой я лучше.", 
            "☕ День начинается с мысли о тебе."
        ]))

async def morning():
    try:
        r = await groq_client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=[
                {"role": "system", "content": f"Короткое утреннее пожелание (1 предложение) для {GIRLFRIEND_NAME} от {YOUR_NAME}."}, 
                {"role": "user", "content": "Утро"}
            ]
        )
        await bot.send_message(GIRLFRIEND_TG_ID, f"☀️ {r.choices[0].message.content.strip()}")
    except Exception as e: 
        print(e)

async def evening():
    try:
        r = await groq_client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=[
                {"role": "system", "content": f"Короткое вечернее пожелание (1 предложение) для {GIRLFRIEND_NAME} от {YOUR_NAME}."}, 
                {"role": "user", "content": "Ночь"}
            ]
        )
        await bot.send_message(GIRLFRIEND_TG_ID, f"🌙 {r.choices[0].message.content.strip()}")
    except Exception as e: 
        print(e)

async def main():
    scheduler.add_job(morning, "cron", hour=9)
    scheduler.add_job(evening, "cron", hour=22)
    scheduler.start()
    print("💕 Бот запущен. Иди в Telegram и напиши /start")
    await dp.start_polling(bot)

if __name__ == "__main__": 
    asyncio.run(main())