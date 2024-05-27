from aiogram import Bot, Dispatcher
from core.handlers.basic import get_start, lessons, get_statistics #create_pay
import asyncio
import logging
from aiogram.filters import Command
from aiogram import F
from core.middlewares.dbmiddleware import DbSession
import asyncpg
from core.handlers.callback import *
from core.utils.commands import set_commands
from core.handlers.callback import callback_check_all_status
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.handlers import apsched
from datetime import datetime
from tzlocal import get_localzone
from core.utils.callbackdata import LessonInfo, HomeworkInfo
import os
from dotenv import load_dotenv, find_dotenv
from core.handlers import homeworks, post_lesson, post_mailing
from core.utils.statesform import StepsForm
from core.middlewares.apschedulermiddleware import SchedulerMiddleware
import json
import logging

load_dotenv(find_dotenv())

host = os.getenv('host')
user = os.getenv('user')
password = os.getenv('password')
db_name = os.getenv('db_name')
port = os.getenv('port')
admin_id = os.getenv('admin_id')
bot_token = os.getenv('bot_token')
database = os.getenv('database')

async def start_bot(bot: Bot):
    # scheduler = AsyncIOScheduler(timezone=str(get_localzone()))
    # scheduler.add_job(apsched.check_all_status, trigger='cron', hour=16,
    #                   minute=1, start_date=datetime.now(), kwargs={'bot': bot, 'pool': pool, 'admin_id': admin_id})
    # scheduler.add_job(apsched.send_message_cron, trigger='cron', hour=16,
    #                   minute=1, start_date=datetime.now(), kwargs={'bot': bot, 'pool': pool, 'admin_id': admin_id})
    # scheduler.start()
    await set_commands(bot)
    await bot.send_message(admin_id, text='Бот запущен! \U0001F38C')

    
async def stop_bot(bot: Bot):
    await bot.send_message(admin_id, text='Бот остановлен! \U0001F3C1')
    


async def create_pool():
    return await asyncpg.create_pool(user=user, password=password, database=database,
                                    host='127.0.0.1', port=5432, command_timeout=60)



async def start():
    try:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - [%(levelname)s] - %(name)s - "
                                "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                            )
        bot = Bot(token=bot_token, parse_mode='HTML')

        pool_connect = await create_pool()
        dp = Dispatcher()
        dp.update.middleware.register(DbSession(pool_connect))
        hourP = 0
        minutesP = 0
        with open('mailing_time.json') as json_file:
            data = json.load(json_file)
            hourP = data['hour']
            minutesP = data['minutes']

        scheduler = AsyncIOScheduler(timezone=str(get_localzone()))
        scheduler.add_job(apsched.check_all_status, trigger='cron', hour=hourP,
                        minute=minutesP, start_date=datetime.now(), kwargs={'bot': bot, 'pool': pool_connect, 'admin_id': admin_id})
        scheduler.add_job(apsched.send_message_cron, trigger='cron', hour=hourP,
                        minute=minutesP, start_date=datetime.now(), kwargs={'bot': bot, 'pool': pool_connect, 'admin_id': admin_id})
        scheduler.start()

        dp.update.middleware.register(SchedulerMiddleware(scheduler))
        print("main")
        dp.startup.register(start_bot)
        dp.shutdown.register(stop_bot)
        dp.message.register(get_start, Command(commands=['start', 'menu']))
        dp.message.register(lessons, Command(commands=['lessons']))
        dp.message.register(get_statistics, Command(commands=['statistics']))
        dp.message.register(homeworks.get_homeworks_panel, Command(commands=['homeworks']))
        dp.message.register(homeworks.post_homework, StepsForm.GET_HOMEWORKS)
        dp.message.register(homeworks.send_comment, StepsForm.GET_DESCRIPTION_HOMEWORK)
        dp.message.register(post_lesson.post_lesson_img, StepsForm.GET_LESSON_IMG)
        dp.message.register(post_lesson.post_lesson_title, StepsForm.GET_LESSON_TITLE)
        dp.message.register(post_lesson.post_lesson_description, StepsForm.GET_LESSON_DESCRIPTION)
        dp.message.register(post_lesson.post_lesson_url, StepsForm.GET_LESSON_URL)
        dp.message.register(post_lesson.post_lesson_year, StepsForm.GET_LESSON_YEAR)
        dp.message.register(post_lesson.post_lesson_month, StepsForm.GET_LESSON_MONTH)
        dp.message.register(post_lesson.post_lesson_day, StepsForm.GET_LESSON_DAY)
        dp.message.register(post_mailing.post_hour, StepsForm.SET_TIME_MAILING_HOUR)
        dp.message.register(post_mailing.post_minutes, StepsForm.SET_TIME_MAILING_MINUTES)
        dp.callback_query.register(select_lesson, LessonInfo.filter(F.type == 'lesson'))
        dp.callback_query.register(get_lesson_statistic, LessonInfo.filter(F.type == 'statistic'))
        dp.callback_query.register(del_lesson, LessonInfo.filter(F.type == 'delLesson'))
        dp.callback_query.register(del_homework, LessonInfo.filter(F.type == 'delHomework'))
        dp.callback_query.register(callback_add_homework, LessonInfo.filter(F.type == 'addHomework'))
        dp.callback_query.register(callback_check_homework, LessonInfo.filter(F.type == 'checkHomework'))
        dp.callback_query.register(callback_get_homework, LessonInfo.filter(F.type == 'getHomework'))
        dp.callback_query.register(callback_add_lesson_access, LessonInfo.filter(F.type == 'lessonAccessAdd'))
        dp.callback_query.register(callback_add_lesson_cancel, LessonInfo.filter(F.type == 'lessonAccessCancel'))
        dp.callback_query.register(callback_homework_validate, HomeworkInfo.filter(F.type == 'validateHomework'))
        dp.callback_query.register(callback_homework_send, HomeworkInfo.filter(F.type == 'sendHomework'))
        dp.callback_query.register(callback_del_lesson_access, DeleteObj.filter(F.type == 'TrueLesson'))
        dp.callback_query.register(callback_del_lesson_cancel, DeleteObj.filter(F.type == 'FalseLesson'))
        dp.callback_query.register(callback_del_homework_access, DeleteObj.filter(F.type == 'TrueHomework'))
        dp.callback_query.register(callback_del_homework_cancel, DeleteObj.filter(F.type == 'FalseHomework'))
        dp.callback_query.register(callback_set_mailingTime_access, MailinTime.filter(F.type == 'TrueMail'))
        dp.callback_query.register(callback_set_mailingTime_cancel, MailinTime.filter(F.type == 'FalseMail'))

        dp.callback_query.register(callback_pay, F.data == 'pay')
        dp.callback_query.register(callback_check_status, F.data == 'check_status')
        dp.callback_query.register(callback_add_homework_panel, F.data == 'add_homework')
        dp.callback_query.register(callback_post_homework, F.data == 'post_homework')
        dp.callback_query.register(callback_post_homework_cancel, F.data == 'post_homework_cancel')
        dp.callback_query.register(callback_clear_homework, F.data == 'clear_homework')
        dp.callback_query.register(callback_check_homeworks, F.data == 'check_homework')
        dp.callback_query.register(callback_add_lesson, F.data == 'add_lesson')
        dp.callback_query.register(callback_del_lesson, F.data == 'del_lesson')
        dp.callback_query.register(callback_mailing_time, F.data == 'mailing_time')
        dp.callback_query.register(callback_set_mailing_time, F.data == 'set_mailing_time')
        dp.callback_query.register(callback_get_mailing_time, F.data == 'get_mailing_time')
        dp.callback_query.register(callback_del_homework, F.data == 'del_homework')
        dp.callback_query.register(callback_get_statistic, F.data == 'get_statistic')
        dp.callback_query.register(callback_get_statistic_lessons, F.data == 'get_statistic_lessons')
        print("main2")
        try:
            await dp.start_polling(bot, pool=pool_connect)
        finally:
            await bot.session.close()
    except Exception as ex:
        print('GGGG')
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        logging.debug(template)
        logging.info(template)
        logging.warning(template)
        logging.error(template)
        logging.critical(template)
if __name__ == "__main__":
    asyncio.run(start())