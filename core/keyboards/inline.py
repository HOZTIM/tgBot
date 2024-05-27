from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.callbackdata import LessonInfo, HomeworkInfo, DeleteObj, MailinTime
from core.utils.sortByDate import sort_by_date

offer_pay = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Купить',
            callback_data='pay'
        ),
        InlineKeyboardButton(
            text='Узнать статус платежа',
            callback_data='check_status'
        )
    ]
])


def admin_panel():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Редактировать домашние задания \U0000270F', callback_data='add_homework')
    keyboard_builder.button(text='Проверить домашние задания\U0001F50E', callback_data='check_homework')
    keyboard_builder.button(text='Добавить новый урок\U0001F5D3', callback_data='add_lesson')
    keyboard_builder.button(text='Удалить урок\U0001F6AE', callback_data='del_lesson') 
    keyboard_builder.button(text='Время рассылки \U000023F0', callback_data='mailing_time') 
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def get_inline_keyboard_mailing_time():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Установить время рассылки \U00002795', callback_data='set_mailing_time')
    keyboard_builder.button(text='Текущее время рассылки \U000023F0', callback_data='get_mailing_time')
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def admin_panel_homeworks():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Редактировать домашние задания \U0000270F', callback_data='add_homework')
    keyboard_builder.button(text='Проверить домашние задания \U0001F50D', callback_data='check_homework')
    keyboard_builder.button(text='Удалить домашние задания \U0001F6AE', callback_data='del_homework')

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def admin_panel_post_homework():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Готово \U00002705', callback_data="post_homework")
    keyboard_builder.button(text='Отменить \U0000274C', callback_data="post_homework_cancel")
    keyboard_builder.button(text='Убрать дз с этого урока \U0001F6AE', callback_data="clear_homework")
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


def get_access_del(lessonId, type):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Подтвердить \U0001F6AE', callback_data=DeleteObj(type=f'True{type}', lessonId=int(lessonId)))
    keyboard_builder.button(text='Отмена \U0000274C', callback_data=DeleteObj(type=f'False{type}',lessonId=int(lessonId)))
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def get_access_post_mailing_time(hour, minutes):
    try:
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(text='Подтвердить \U0001F6AE', callback_data=MailinTime(type=f'TrueMail', hour=int(hour), minutes=int(minutes)))
        keyboard_builder.button(text='Отмена \U0000274C', callback_data=MailinTime(type=f'FalseMail', hour=int(hour), minutes=int(minutes)))
        keyboard_builder.adjust(1)
        return keyboard_builder.as_markup()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"

def get_access_add_lesson(id):    
    try:
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(text="Добавить \U00002705", callback_data=LessonInfo(id=str(id), type="lessonAccessAdd", clientId=0))
        keyboard_builder.button(text="Отмена \U0000274C", callback_data=LessonInfo(id=str(id), type="lessonAccessCancel", clientId=0))
        keyboard_builder.adjust(1)
        return keyboard_builder.as_markup()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"

def get_inline_keyboard(lessons, typeLesson, clientId):
    keyboard_builder = InlineKeyboardBuilder()
    lessons.sort(key=sort_by_date)
    for lesson in lessons:
        keyboard_builder.button(text=lesson.title, callback_data=LessonInfo(id=str(lesson.id), type=str(typeLesson), clientId=int(clientId)))
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def get_inline_keyboard_statistic():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Общая статистика \U0001F4C9', callback_data="get_statistic")
    keyboard_builder.button(text='Статистика по урокам \U0001F4CA', callback_data="get_statistic_lessons")
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def get_inline_keyboard_homework_done(studentId, homeworkId):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Отлично \U0001F44D', callback_data=HomeworkInfo(studentId=studentId, homeworkId=homeworkId, isDone=True, type="validateHomework"))
    keyboard_builder.button(text='Плохо \U0001F44E', callback_data=HomeworkInfo(studentId=studentId, homeworkId=homeworkId, isDone=False, type="validateHomework"))
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def get_inline_keyboard_homework_send(studentId, homeworkId):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Отправить на проверку \U00002709', callback_data=HomeworkInfo(studentId=studentId, homeworkId=homeworkId, isDone=False, type="sendHomework"))
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
