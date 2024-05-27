from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='menu',
            description='Меню \U0001F38C'
        ),
        # BotCommand(
        #     command='pay',
        #     description='Оплатить курс'
        # ),
        BotCommand(
            command='lessons',
            description='Уроки \U0001F4BC'
        ),
        BotCommand(
            command='homeworks',
            description='Домашние работы \U0001F4EC'
        ),
        BotCommand(
            command='statistics',
            description='Статистика \U0001F4C8'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())