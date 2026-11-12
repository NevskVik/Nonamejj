import asyncio, json, os, time
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

TOKEN = os.environ["1780244857:5k0zivNAouNR5ZdqVb-oWHgCX2EYZJA94H_"]
CHAT = os.environ.get("CHAT_ID", "@OHUENKO")
if CHAT.lstrip("-").isdigit():
    CHAT = int(CHAT)
REPORT = 1000  # публикация примерно раз в 30 минут
NAMES = {}     # "9000000000000017": "Название подарка"

DROP = ("@OHUENKOchat наш чат\nСоздатель @skiding\n"
        "Если хотите помочь то можете дать вклад в проект")
NONE = ("@OHUENKOchat наш чат\nСоздатель @skiding\n"
        "Если хотите помочь то можете поддержать проект")

bot = Bot(TOKEN, session=AiohttpSession(
    api=TelegramAPIServer.from_base("http://2.27.21.133:8081")))

def load():
    try:
        return json.load(open("state.json"))
    except Exception:
        return {"seen": None, "pending": [], "last": 0}

def build(new):
    if not new:
        return ("❌Сегодня нихуя не было.❌\n\n"
                "Ничего не добавили но мы ждём\n\n" + NONE)
    parts = ["‼️‼️Сегодня был дроп.‼️‼️\n"]
    for g in new:
        name = NAMES.get(g["id"], f"подарок {g['id']} ({g['stars']}⭐)")
        qty = f"{g['rem']} из {g['total']}" if g["total"] else "Есть"
        parts.append(f"Добавили {name}\nКол-во. {qty}\n")
    return "\n".join(parts) + "\n" + DROP

async def main():
    st = load()
    now = time.time()
    gifts = (await bot.get_available_gifts()).gifts
    if st["seen"] is None:
        st["seen"] = [g.id for g in gifts]
        st["last"] = now
    else:
        for g in gifts:
            if g.id not in st["seen"]:
                st["seen"].append(g.id)
                st["pending"].append({"id": g.id, "stars": g.star_count,
                    "rem": g.remaining_count, "total": g.total_count})
    if now - st["last"] >= REPORT:
        await bot.send_message(CHAT, build(st["pending"]))
        st["pending"], st["last"] = [], now
    json.dump(st, open("state.json", "w"))
    await bot.session.close()

asyncio.run(main())
