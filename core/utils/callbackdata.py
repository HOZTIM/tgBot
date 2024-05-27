from aiogram.filters.callback_data import CallbackData

class LessonInfo(CallbackData, prefix='lesson'):
    id: str
    type: str
    clientId: int

class HomeworkInfo(CallbackData, prefix='homework'):
    studentId: int
    homeworkId: int
    isDone: bool
    type: str

class DeleteObj(CallbackData, prefix='DeleteObj'):
    type: str
    lessonId: int

class MailinTime(CallbackData, prefix='MailingTime'):
    type: str
    hour: int
    minutes: int
