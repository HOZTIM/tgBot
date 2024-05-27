from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import os
from core.keyboards.inline import admin_panel_homeworks, get_inline_keyboard, admin_panel_post_homework
from core.utils.dbconnect import Request
from datetime import datetime
from core.utils.lesson import Lesson
from core.keyboards.inline import offer_pay
from aiogram import Bot
async def get_homeworks_panel(message: Message, request: Request):
    try:
        user_id = message.from_user.id
        admin_id = os.getenv('admin_id')
        if str(user_id) == str(admin_id):
            await message.answer(f'Рад тебя видеть <b>администратор</b>, что нужно сделать? \U0001F4EC', reply_markup=admin_panel_homeworks())
        else:
            boolP = await request.get_status_client(user_id)
            if boolP:
                year = datetime.now().year
                month = datetime.now().month
                day = datetime.now().day

                all_lesson = await request.get_all_lesson_for_user(user_id)
                list_Lessons = [dict(row) for row in all_lesson]
                lessons = []
                for lesson in list_Lessons:
                    yearL = int(str(lesson['datelesson']).split('-')[0])
                    monthL = int(str(lesson['datelesson']).split('-')[1])
                    dayL = int(str(lesson['datelesson']).split('-')[2])
                    if(datetime(year, month, day) >= datetime(yearL, monthL, dayL)):
                        newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
                        lessons.append(newLesson)
                if len(list_Lessons) > 0:
                    lesson = await request.get_next_lesson_for_user(user_id)
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
                if len(lessons)>0:
                    await message.answer(
                        f'<b>Выберите урок, задания к которому хотите выполнить</b> \U0000270F',
                        reply_markup=get_inline_keyboard(lessons, "getHomework", message.from_user.id)
                    )
                else:
                    await message.answer(
                        f'<b>На данный момент нет домашних заданий</b> \U0001F937',
                        reply_markup=get_inline_keyboard(lessons, "getHomework", message.from_user.id)
                    )
            else:
                await message.answer(
                    f'<b>Необходимо оплатить курсы, чтобы получить доступ к домашним заданиям</b>',
                    reply_markup=offer_pay
                )
    except:
        await message.answer(f'<s>Ошибка, попробуйте снова</s>')
    
async def post_homework(message: Message, state: FSMContext):
    try:
        context_data = await state.get_data()
        context_text = context_data.get('text')
        await state.update_data(text=context_text+message.text)
        isFinish = context_data.get('isFinish')
        if isFinish:
            await state.update_data(isFinish=True)
        else:
            await message.answer(f'<b>Нажмите кнопку, чтобы закончить отправку</b> \U0000270F', reply_markup=admin_panel_post_homework())
            await state.update_data(isFinish=True)
    except:
        await message.answer(f'<s>Ошибка при отправке</s>')

async def send_comment(message: Message,  bot: Bot, state: FSMContext):
    try:
        admin_id = os.getenv('admin_id')
        text = message.text
        context_data = await state.get_data()
        studentId = context_data.get('studentId')
        lessonTitle = context_data.get('lessonTitle')
        await bot.send_message(studentId, f'Домашняя работа к уроку <b>"{lessonTitle}"</b> не засчитывается. \U0000274C\n\U00002709 Комментарий куратора: <i>{text}</i>')
        await bot.send_message(admin_id, f'Комментарий отправлен \U00002705')
    except:
        await bot.send_mesage(message.from_user.id, "<s>Пользователь заблокировал бота</s>")
    
