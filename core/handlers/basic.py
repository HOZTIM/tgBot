from aiogram import Bot, types
from aiogram.types import Message
from core.utils.dbconnect import Request
from core.keyboards.inline import offer_pay, admin_panel, get_inline_keyboard, get_inline_keyboard_statistic
from datetime import datetime
from core.utils.lesson import Lesson
import os
from dotenv import load_dotenv, find_dotenv
from core.utils.sortByDate import sort_by_date

load_dotenv(find_dotenv())

admin_id = os.getenv('admin_id')


async def get_statistics(message: Message, bot: Bot, request: Request):
    tgid = message.from_user.id
    boolP = await request.get_status_client(tgid)
    if (str(message.from_user.id) == str(admin_id)):
        await message.answer(
            f'<b>Что нас интересует?</b>\U0001F440',
            reply_markup=get_inline_keyboard_statistic()
        )
    elif boolP:
        all_lesson = await request.get_all_lesson()
        list_Lessons = [dict(row) for row in all_lesson]
        lessons = []
        answerUser = f"<b>Статистика</b> \U0001F4CA\n"
        for lesson in list_Lessons:
            newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
            lessons.append(newLesson)
        lessons.sort(key=sort_by_date)
        for lesson in lessons:
            isDone = await request.check_homeworks_isDone(lesson.id, tgid, True)
            if isDone:
                answerUser += lesson.title + "<b> - Отлично</b> \U00002705\n"
            else:
                answerUser += lesson.title + "<b> - Не выполнено \U000026A0\n</b>"
        if len(lessons) > 0:
            await message.answer(
                answerUser
            )
        else:
            await message.answer(
                "<b>Статистики пока нет</b>\U0001F937"
            )
    else:
        await message.answer(
            f'<b>Необходимо оплатить курсы, чтобы получить доступ к урокам</b>',
            reply_markup=offer_pay
        )

async def lessons(message: Message, bot: Bot, request: Request):
    tgid = message.from_user.id
    boolP = await request.get_status_client(tgid)
    if (str(message.from_user.id) == str(admin_id)):
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day

        all_lesson = await request.get_all_lesson()
        list_Lessons = [dict(row) for row in all_lesson]
        lessons = []
        for lesson in list_Lessons:
            yearL = int(str(lesson['datelesson']).split('-')[0])
            monthL = int(str(lesson['datelesson']).split('-')[1])
            dayL = int(str(lesson['datelesson']).split('-')[2])

            newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
            lessons.append(newLesson)

        if len(lessons) > 0:
            await message.answer(
                f'<b>Выбери урок, который ты ищешь)</b> \U0001F50E',
                reply_markup=get_inline_keyboard(lessons, 'lesson', message.from_user.id)
            )
        else:
            await message.answer(
                f'<b>Уроков нет</b> \U0001F937'
            )
    elif boolP:
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day

        all_lesson = await request.get_all_lesson_for_user(tgid)
        list_Lessons = [dict(row) for row in all_lesson]
        lessons = []
        for lesson in list_Lessons:
            yearL = int(str(lesson['datelesson']).split('-')[0])
            monthL = int(str(lesson['datelesson']).split('-')[1])
            dayL = int(str(lesson['datelesson']).split('-')[2])
            if(datetime(year, month, day) >= datetime(yearL, monthL, dayL)):
                newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
                lessons.append(newLesson)
        if len(list_Lessons) != 0:
            lesson = await request.get_next_lesson_for_user(tgid)
            if lesson:
                yearL = int(str(lesson['datelesson']).split('-')[0])
                monthL = int(str(lesson['datelesson']).split('-')[1])
                dayL = int(str(lesson['datelesson']).split('-')[2])
                if(datetime(year, month, day) >= datetime(yearL, monthL, dayL)):
                    newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
                    lessons.append(newLesson)
        if len(list_Lessons) == 0:
            list_Lessons = await request.get_first_lesson_for_user()
            for lesson in list_Lessons:
                yearL = int(str(lesson['datelesson']).split('-')[0])
                monthL = int(str(lesson['datelesson']).split('-')[1])
                dayL = int(str(lesson['datelesson']).split('-')[2])
                if(datetime(year, month, day) >= datetime(yearL, monthL, dayL)):
                    newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
                    lessons.append(newLesson)
        if len(lessons) > 0:
            await message.answer(
                f'<b>Выбери урок, который ты ищешь)</b> \U0001F50E',
                reply_markup=get_inline_keyboard(lessons, 'lesson', message.from_user.id)
            )
        else:
            await message.answer(
                f'<b>Уроков нет</b> \U0001F937'
            )
    else:
        await message.answer(
            f'Необходимо оплатить курсы, чтобы получить доступ к урокам',
            reply_markup=offer_pay
        )


async def get_start(message: Message, bot: Bot, request: Request):
    print("kyy")
    if (str(message.from_user.id) == str(admin_id)):
        print("kyy2")
        await message.answer(
            f'Привет администратор <b>{message.from_user.first_name}</b>\U0001F590. Рад тебя видеть!\U0001F604',
            reply_markup = admin_panel()
        )
        try:
            data = await request.get_all_by_status('yes')
            text = f'<b>На данный момент {len(data)} \U0001F393 подписанных пользователей.</b>'
            await bot.send_message(message.from_user.id, text)
        except:
            text = '<b><s>Извините сервер не отвечает</s></b>'
            await bot.send_message(message.from_user.id, text)
    else:
        await message.answer(
            f'Привет <b>{message.from_user.first_name}</b>\U0001F590. Рад тебя видеть!\U0001F604'
        )
        try:
            res = await request.check_id(message.from_user.id)
            if res == 'SELECT 0':
                await request.add_client(message.from_user.id, message.from_user.first_name)

            res = await request.check_status(message.from_user.id , 'yes')
            if res == 'SELECT 0':
                await message.answer(
                    f'Не желаете ли вы приобрести наш курс?',
                    reply_markup = offer_pay
                )
        except:
            await message.answer(
                f'<b>{message.from_user.first_name}</b> не удалось зарегистрировать. <s>Ошибка на сервере</s>',
            )
