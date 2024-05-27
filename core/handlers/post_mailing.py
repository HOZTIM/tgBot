from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.utils.statesform import StepsForm
import re
from core.keyboards.inline import get_access_post_mailing_time
import json

async def post_hour(message: Message,  bot: Bot, state: FSMContext):
    try:
        hour = message.text
        # result = re.match(r'^\d{2}$', hour)
        if int(hour) < 24 and int(hour) >= 0:
            await state.update_data(hour=hour)
            await bot.send_message(message.from_user.id, "\U000023F0 - Введите минуты в формате 0-59 \U000023F0")
            await state.set_state(StepsForm.SET_TIME_MAILING_MINUTES)
        else:
            await bot.send_message(message.from_user.id, "\U000023F0 - Попробуйте еще раз, например отправьте число от 0 до 23 без пробелов \U000023F0")
    except:
        await bot.send_message(message.from_user.id, "<s>Ошибка при добавлении заголовка</s>")

async def post_minutes(message: Message,  bot: Bot, state: FSMContext):
    try:
        minutes = message.text
        # result = re.match(r'^\d{2}$', minutes)
        if int(minutes) < 60 and int(minutes) >= 0:
            await state.update_data(minutes=minutes)
            context_data = await state.get_data()
            hour = context_data.get('hour')
            minutes = context_data.get('minutes')
            # to_json = {'hour': hour, 'minutes': minutes}
            # with open('mailing_time.json', 'w') as f:
            #     f.write(json.dumps(to_json))
            await bot.send_message(
                message.from_user.id, 
                f'Подтверждение:\nВремя рассылки: {hour}:{minutes}, все правильно?',
                reply_markup=get_access_post_mailing_time(hour, minutes)
            )
        else:
            await bot.send_message(message.from_user.id, "\U000023F0 - Попробуйте еще раз, например отправьте число от 0 до 59 без пробелов \U000023F0")
    except:
        await bot.send_message(message.from_user.id, "<s>Ошибка при добавлении заголовка</s>")

