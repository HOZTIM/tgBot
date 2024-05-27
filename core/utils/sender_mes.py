from aiogram import Bot
import asyncpg
from datetime import datetime, timedelta

class SenderMes:
    def __init__(self, bot: Bot, connector: asyncpg.pool.Pool):
        self.bot = bot,
        self.connector = connector

    async def get_lesson_today(self):
        dateToday = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day)
        async with self.connector.acquire() as connect:
            query = f"select * from lesson where datelesson = '{dateToday}'"
            return await connect.fetch(query)
         