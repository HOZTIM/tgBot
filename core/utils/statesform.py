from aiogram.fsm.state import StatesGroup, State

class StepsForm(StatesGroup):
    GET_HOMEWORKS = State()
    GET_LESSON_IMG = State()
    GET_LESSON_TITLE = State()
    GET_LESSON_DESCRIPTION = State()
    GET_LESSON_URL = State()
    GET_LESSON_YEAR = State()
    GET_LESSON_MONTH = State()
    GET_LESSON_DAY = State()
    # Комментарий к дз
    GET_DESCRIPTION_HOMEWORK = State()
    # Время рассылки
    SET_TIME_MAILING_HOUR = State()
    SET_TIME_MAILING_MINUTES = State()

