from aiogram import Bot
from aiogram.types import CallbackQuery, FSInputFile
from core.utils.pay import payment, check_payment
from core.utils.dbconnect import Request
from core.utils.callbackdata import LessonInfo, HomeworkInfo, DeleteObj, MailinTime
from core.utils.statesform import StepsForm
from aiogram.fsm.context import FSMContext
from core.keyboards.inline import get_inline_keyboard, get_inline_keyboard_homework_done, get_inline_keyboard_homework_send, get_access_del, get_inline_keyboard_mailing_time
from datetime import datetime
from core.utils.lesson import Lesson
import os
import json
from core.utils.sortByDate import sort_by_date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.handlers import apsched


async def get_lesson_statistic(call: CallbackQuery, bot: Bot, callback_data: LessonInfo, request: Request):
    try:
        lessonId = callback_data.id
        clientId = callback_data.clientId
        admin_id = os.getenv('admin_id')
        if str(clientId) == str(admin_id):
            countStudents = await request.get_count_students()
            countStudentsIsDone = await request.get_count_students_lesson(lessonId, 'YES')
            await call.message.answer(f'<b>Статистика:</b> \nКоличество студентов: <b>{countStudents} \U0001F393</b>\nВыполнили задание: <b>{countStudentsIsDone}</b> \U00002611') ####доделать####
            await call.answer()
    except:
        text = '<s>Ошибка при получение статистики</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def select_lesson(call: CallbackQuery, bot: Bot, callback_data: LessonInfo, request: Request):
    try:
        lessonId = callback_data.id
        clientId = callback_data.clientId
        admin_id = os.getenv('admin_id')

        all_lesson = await request.get_all_lesson()
        list_Lessons = [dict(row) for row in all_lesson]
        lessons = []
        for lesson in list_Lessons:
            newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
            lessons.append(newLesson)
        lessons.sort(key=sort_by_date)
        indexOurLesson = -1
        i = -1
        for item in lessons:
            i = i + 1
            if str(item.id) == str(lessonId):
                indexOurLesson = i
        indexOurLesson = indexOurLesson - 1
        isDone = False

        if str(call.from_user.id) == str(admin_id):
            isDone = True
        elif indexOurLesson > 0:
            isDone = await request.get_homeworks_isDone(lessons[indexOurLesson].id, clientId)
        elif indexOurLesson == 0:
            isDone = True
        data = await request.get_lesson_by_id(lessonId)
        for lesson in data:
            photo_mg = FSInputFile(fr'D:\bot2\core\src\photo\lesson{lesson["id"]}.jpg')
            answer = f'{lesson["title"]}\n \n{lesson["description"]}\n\nСсылка на урок: \n{lesson["url"]}\n \nДата урока: {lesson["datelesson"]}'
            await bot.send_photo(call.from_user.id, photo_mg, caption=answer)
            await call.answer()
    except:
        text = '<s>Ошибка при получение урока</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def callback_check_all_status(call: CallbackQuery, bot: Bot, request: Request):
    try:
        text = 'Проверка началась!'
        await bot.send_message(call.from_user.id, text)
        data = await request.get_all_by_status('waiting')
        text = f'На данный момент <b>{len(data)}</b> платежей в процессе.'
        await bot.send_message(call.from_user.id, text)
        for payment in data:
            try:
                if(await check_payment(payment['paymentid'])):
                    await request.update_status(payment['paymentid'], 'yes')
                    text = f'Оплата прошла успешно'
                    await bot.send_message(payment['tgid'], text)
                    await call.message.answer(
                        f'В результате проверки выяснилось, что пользователь с id = <b>{payment["tgid"]}</b> успешно оплатил заказ',
                    )
                else:
                    await request.update_status(payment['paymentid'], 'no')
                    text = f'<s>Оплата не прошла</s>'
                    await bot.send_message(payment['tgid'], text)
                    await call.message.answer(
                        f'В результате проверки выяснилось, что пользователь с id = <b>{payment["tgid"]}</b> не смог оплатить заказ',
                    )
            except:
                await call.message.answer(
                    f'<s>Извините, у нас технические проблемы</s>',
                )
        text = 'Проверка закончилась!'
        await bot.send_message(call.from_user.id, text)
        await call.answer()
    except:
        text = '<s>Извините сервер не отвечает</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()


async def callback_check_status(call: CallbackQuery, request: Request):
    user_id = str(call.from_user.id)
    try:
        res = await request.check_status_user(user_id)
        data = [dict(row) for row in res]
        text = ''
        if(len(data) == 0):
            text = 'Нет информации о вашем платеже'
            await call.message.answer(text)
        elif(len(data) > 1):
            text = 'Вы пытались оплатить более <b>одного раза</b>, вот данные о транзакциях'
            await call.message.answer(text) 
            for item in data:
                if(item['status'] == 'yes'):
                    text = 'Платеж успешно прошел \U00002705'
                elif(item['status'] == 'no'):
                    text = 'Платеж не прошел \U0000274C'
                elif(item['status'] == 'waiting'):
                    text = 'Ожидаем пока средства поступят к нам на счёт \U000023F3'
                await call.message.answer(text)

        elif(len(data) == 1):
            for item in data:
                if(item['status'] == 'yes'):
                    text = 'Платеж успешно прошел \U00002705'
                elif(item['status'] == 'no'):
                    text = 'Платеж не прошел \U0000274C'
                elif(item['status'] == 'waiting'):
                    text = 'Ожидаем пока средства поступят к нам на счёт \U000023F3'

            await call.message.answer(text)
        await call.answer()
    except:
        text = '<s>Извините сервер не отвечает</s>'
        await call.message.answer(text)
        await call.answer()

async def callback_pay(call: CallbackQuery, bot: Bot, request: Request):
    user_id = str(call.from_user.id)
    res = await request.check_status(user_id, 'yes')
    if (res == "SELECT 0"):
        payment_data  = payment("100","тестовый платеж")
        payment_id = payment_data['id']
        payment_url = (payment_data['confirmation'])['confirmation_url']
        try:
            await request.add_payment(100, user_id, 'waiting', payment_id)
            await call.message.answer(
                f'Ссылка для оплаты курса: {payment_url}',
            )
            await call.answer()
            if(await check_payment(payment_id)):
                await call.message.answer(
                    f'Оплата прошла успешно',
                )
                await request.update_status(payment_id, 'yes')
                all_lesson = await request.get_all_lesson()
                list_Lessons = [dict(row) for row in all_lesson]
                for lesson in list_Lessons:
                    homeworkReserve = await request.get_homeworkReserve(lesson['id'])
                    if len(homeworkReserve) > 0:
                        await request.add_homework(user_id, homeworkReserve[0]['urlhomeworks'], lesson['id'])
                        await request.del_homeworkReserve(homeworkReserve[0]['urlhomeworks'], lesson['id'])
            else:
                await call.message.answer(
                    f'<s>Оплата не прошла</s>',
                )
                await request.update_status(payment_id, 'no')
        except:
            await call.message.answer(
                f'<s>Извините, у нас технические проблемы</s>',
            )
            await call.answer()
    else:
        await call.message.answer(
            f'Вы уже оплатили курс',
        )
        await call.answer()

    

async def callback_add_homework_panel(call: CallbackQuery, request: Request, state: FSMContext):
    try:
        all_lesson = await request.get_all_lesson()
        list_Lessons = [dict(row) for row in all_lesson]
        lessons = []
        for lesson in list_Lessons:
            newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
            lessons.append(newLesson)
        if len(lessons) > 0:
            await call.message.answer(
                f'<b>Выберите урок</b> домашние задания к которому необходимо редактировать \U0000270F',
                reply_markup=get_inline_keyboard(lessons, 'addHomework', call.from_user.id)
            )
        else:
            await call.message.answer(
                f'<b>Уроков нет</b> \U0001F937'
            )
        await call.answer()
    except:
        await call.message.answer(
            f'<s>Ошибка при добавление домашнего задания</s>',
        )
        await call.answer()



async def callback_add_homework(call: CallbackQuery, bot: Bot, callback_data: LessonInfo, request: Request, state: FSMContext):
    try: 
        admin_id = os.getenv('admin_id')
        textNull = ''
        id = callback_data.id
        await state.update_data(lessonId=id)
        await state.update_data(text=textNull)
        await state.update_data(isFinish=False)
        data = await request.get_lesson_by_id(id)
        photo_mg = FSInputFile(fr'D:\bot2\core\src\photo\lesson{id}.jpg')
        for lesson in data:
            await bot.send_photo(admin_id, photo_mg ,caption=f'<b>Добавить домашнее задание к уроку:</b>\n\n<b>{lesson["title"]}</b>\n\nСсылка на урок: \n<b>{lesson["url"]}</b>\nИнструкция: Отправь мне текстовый файл с <b>JSON структурой</b>.')
        await state.set_state(StepsForm.GET_HOMEWORKS)
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при добавлении домашнего задания</s>')
        await call.answer()

async def callback_clear_homework(call: CallbackQuery,  bot: Bot, state: FSMContext, request: Request):
    try: 
        context_data = await state.get_data()
        lessonId = context_data.get('lessonId')
        await request.clear_homeworks_from_lesson(lessonId)

        admin_id = os.getenv('admin_id')
        lessonTitle = ''
        data = await request.get_lesson_by_id(lessonId)
        for lesson in data:
            lessonTitle = lesson["title"]
        await bot.send_message(admin_id, f'Домашние задания удалены с урока под названием <b>{lessonTitle}</b> \U0001F6AE')
        await state.clear()        
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при удаление домашнего задания</s>')
        await call.answer()

async def callback_post_homework_cancel(call: CallbackQuery,  bot: Bot, state: FSMContext):
    try: 
        admin_id = os.getenv('admin_id')
        await state.clear()        
        await bot.send_message(admin_id, '<b>Отменено</b> \U0000274C')
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при отмене добавления нового домашнего задания</s>')
        await call.answer()
        
async def callback_post_homework(call: CallbackQuery,  bot: Bot, state: FSMContext, request: Request):
    try:
        context_data = await state.get_data()
        context_text = context_data.get('text')
        lessonId = context_data.get('lessonId')
        homeworkUrls = json.loads(context_text)
        dataClients = await request.get_all_by_status('yes')

        count = 0
        boolAccess = True
        for payment in dataClients:
            if len(homeworkUrls) > 0:
                homework = homeworkUrls[0]
                if await request.check_homework(payment['tgid'], lessonId):
                        await request.add_homework(payment['tgid'], homework['url'], lessonId)
                        homeworkUrls.pop(0)
                        count += 1
            else:
                boolAccess = False
                await call.message.answer(
                    f'не хватило домашних заданий, <b>{count}</b> штук добавлено успешно, осталось ещё <b>{await request.get_count_need_homework_for_lesson()}</b>',
                )
                break
        if boolAccess:
            await call.message.answer(
                f'<b>Домашние задания прикреплены успешно</b> \U00002705',
            )
        if len(homeworkUrls) > 0:
            countHomework = 0
            for homeworkurl in homeworkUrls:
                await request.add_homeworkReserve('empty', homeworkurl['url'], lessonId)
                countHomework += 1
            homeworkReserve = await request.get_homeworkReserve(lessonId)
            await call.message.answer(
                f'Есть лишние домашние задания, в количестве <b>{countHomework}</b>, они автоматически прикрепятся к новым ученикам \U00002705 \nВсего запас домашних заданий к этому уроку: {len(homeworkReserve)}',
            )
        await state.clear() 
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при добавлении нового домашнего задания</s>')
        await state.clear()
        await call.answer()
    
async def callback_check_homeworks(call: CallbackQuery, request: Request):
    try:
        all_lesson = await request.get_all_lesson()
        list_Lessons = [dict(row) for row in all_lesson]
        lessons = []
        listid = []
        list_Lessons_t = await request.get_lesson_issend(True)
        for itemid in list_Lessons_t:
            listid.append(itemid['id'])
        for lesson in list_Lessons:
            if lesson['id'] in listid:
                newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
                lessons.append(newLesson)
        if len(lessons) > 0:
            await call.message.answer(
                f'<b>Выберите урок</b> задания к которому хотите проверить\U0001F50E',
                reply_markup=get_inline_keyboard(lessons, 'checkHomework', call.from_user.id)
            )
        else:
            await call.message.answer(
                f'<b>Нечего проверять</b>\U0001F937',
            )
        await call.answer()
    except:
        await call.message.answer('Домашних заданий на выбранный урок не запланировано')
        await call.answer()


async def callback_check_homework(call: CallbackQuery, callback_data: LessonInfo, request: Request):
    try:
        lessonId = callback_data.id
        res = await request.get_homeworks_by_lessonId(lessonId, False, True)
        data = [dict(row) for row in res]
        if len(data) > 0:
            for homework in data:
                lessonTitle = ''
                data = await request.get_lesson_by_id(homework["lessonid"])
                for lesson in data:
                    lesson = await request.get_lesson_by_id(homework["lessonid"])
                    lessonTitle = lesson[0]["title"]
                name = await request.get_studentName_by_id(homework["clientid"])
                await call.message.answer(f'<b>{lessonTitle}</b>\nИмя студента в телеграм: <b>{name}</b>\nId студента в телеграм: <b>{homework["clientid"]}</b>\nСcылка: <b>{homework["urlhomeworks"]}</b>',reply_markup=get_inline_keyboard_homework_done(homework["clientid"], homework["id"]))
        else:
            await call.message.answer('Домашние задания на этот урок <b>проверены</b>, либо их <b>нет</b>')
        await call.answer()
    except:
        await call.message.answer('<s>Ошибка при проверке домашних заданий</s>')
        await call.answer()
    
async def callback_get_homework(call: CallbackQuery, callback_data: LessonInfo, request: Request):
    try:
        lessonId = callback_data.id
        lessonTitle = ''
        data = await request.get_lesson_by_id(lessonId)
        for lesson in data:
            lessonTitle = lesson["title"]
        homework = await request.get_homeworks_by_studentId(lessonId, call.from_user.id, False)
        if len(homework)>0:
            await call.message.answer(f'\U0001F4CE Ссылка для выполнения домашнего задания к уроку:\n<b>{lessonTitle}</b>\n\n<b>{homework[0]["urlhomeworks"]}</b>', reply_markup=get_inline_keyboard_homework_send(call.from_user.id, homework[0]["id"]))
            await call.answer()
        else:
            homework2 = await request.get_homeworks_by_studentId(lessonId, call.from_user.id, True)
            if len(homework2)>0:
                await call.message.answer(f'Успешно выполнено: <b>{lessonTitle}</b>\n\n<b>{homework2[0]["urlhomeworks"]}</b>')
            else:
                await call.message.answer('Домашнее задание на выбранный урок пока отсутствует')
        await call.answer()
    except:
        await call.message.answer('Домашнего задания ещё нет')
        await call.answer()

async def callback_homework_validate(call: CallbackQuery, bot: Bot, callback_data: HomeworkInfo, request: Request, state: FSMContext):
    try:
        studentId = callback_data.studentId
        isDone = callback_data.isDone
        homeworkId = callback_data.homeworkId
        studentName = await request.get_studentName_by_id(studentId)
        await request.set_homework_isDone(isDone, homeworkId)
        await request.send_homework(False, studentId,homeworkId)
        homework = await request.get_homeworks_by_id(homeworkId)
        lessonId = homework['lessonid']
        dataLessons = await request.get_lesson_by_id(lessonId)
        if isDone:
            for lesson in dataLessons:
                await bot.send_message(studentId, f'Вы <b>успешно</b> выполнили домашнюю работу к уроку <b>"{lesson["title"]}"</b>')
            await call.message.answer(f'Студент <b>{studentName}</b> успешно выполнил задание к уроку ')
        else:
            await call.message.answer(f'Работа студента <b>{studentName}</b> не засчитывается.\nНапишите комментарий: <b>(не более одного сообщения)</b>: \U00002709')
            await state.update_data(studentId=studentId)
            for lesson in dataLessons:
                await state.update_data(lessonTitle=lesson["title"])
            await state.set_state(StepsForm.GET_DESCRIPTION_HOMEWORK)
        await call.answer()
    except:
        await call.message.answer('<s>Ошибка при оценке работы</s>')
        await call.answer()

async def callback_homework_send(call: CallbackQuery, bot: Bot, callback_data: HomeworkInfo, request: Request, state: FSMContext):
    try:
        studentId = callback_data.studentId
        homeworkId = callback_data.homeworkId
        await request.send_homework(True, studentId,homeworkId)
        await call.message.answer('<b>Работа успешно отправлена</b>')
        await call.answer()
    except:
        await call.message.answer('<s>Ошибка при отправке работы</s>')
        await call.answer()

async def callback_add_lesson(call: CallbackQuery,  bot: Bot, state: FSMContext, request: Request):
    try: 
        admin_id = os.getenv('admin_id')
        await state.set_state(StepsForm.GET_LESSON_TITLE)
        await bot.send_message(admin_id, '\U00000031 - Введите заголовок нового урока \U0001F5D3')
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при добавлении нового урока</s>')
        await call.answer()

async def callback_del_homework(call: CallbackQuery,  bot: Bot, request: Request):
    try:
        all_lesson = await request.get_all_lesson()
        list_Lessons = [dict(row) for row in all_lesson]
        lessons = []

        for lesson in list_Lessons:
            newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
            lessons.append(newLesson)
        if len(lessons) > 0:
            await call.message.answer(
                f'<b>Выберите урок, домашние задания к которому нужноу удалить</b> \U0001F6AE',
                reply_markup=get_inline_keyboard(lessons, 'delHomework', call.from_user.id)
            )
        else:
            await call.message.answer(
                f'<b>Уроков нет</b> \U0001F937'
            )
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при выборе урока</s>')
        await call.answer()

async def callback_get_mailing_time(call: CallbackQuery,  bot: Bot):
    try:
        hourP = 0
        minutesP = 0
        with open('mailing_time.json') as json_file:
            data = json.load(json_file)
            hourP = data['hour']
            minutesP = data['minutes']
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, f'Время рассылки: {hourP}:{minutesP}')
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при добавлении нового урока</s>')
        await call.answer()

async def callback_set_mailing_time(call: CallbackQuery,  bot: Bot, state: FSMContext):
    try: 
        admin_id = os.getenv('admin_id')
        await state.set_state(StepsForm.SET_TIME_MAILING_HOUR)
        await bot.send_message(admin_id, '\U000023F0 - Введите час в формате 0-23 \U000023F0')
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при добавлении нового урока</s>')
        await call.answer()

async def callback_mailing_time(call: CallbackQuery,  bot: Bot):
    try:
        await call.message.answer(
            f'<b>Что нужно сделать?</b> \U000023F0',
            reply_markup=get_inline_keyboard_mailing_time()
        )
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при установке времени</s>')
        await call.answer()

async def callback_del_lesson(call: CallbackQuery,  bot: Bot, request: Request):
    try:
        all_lesson = await request.get_all_lesson()
        list_Lessons = [dict(row) for row in all_lesson]
        lessons = []

        for lesson in list_Lessons:
            newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
            lessons.append(newLesson)
        if len(lessons) > 0:
            await call.message.answer(
                f'<b>Выберите урок, который нужно удалить</b> \U0001F6AE',
                reply_markup=get_inline_keyboard(lessons, 'delLesson', call.from_user.id)
            )
        else:
            await call.message.answer(
                f'<b>Уроков нет</b> \U0001F937'
            )
        await call.answer()
    except:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, '<s>Ошибка при выборе урока</s>')
        await call.answer()


async def callback_set_mailingTime_cancel(call: CallbackQuery, bot: Bot):
    try:
        await call.message.answer(
            f'<b>Отменено</b> \U0000274C'
        )
        await call.answer()
    except:
        text = '<s>Ошибка</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def callback_set_mailingTime_access(call: CallbackQuery, bot: Bot, callback_data: MailinTime, apscheduler: AsyncIOScheduler, pool):
    try:
        print("start callback_set_mailingTime_access")
        admin_id = os.getenv('admin_id')
        hour = callback_data.hour
        minutes = callback_data.minutes
        to_json = {'hour': hour, 'minutes': minutes}
        with open('mailing_time.json', 'w') as f:
            f.write(json.dumps(to_json))
        apscheduler.remove_all_jobs()
        apscheduler.add_job(apsched.check_all_status, trigger='cron', hour=hour,
                        minute=minutes, start_date=datetime.now(), kwargs={'bot': bot, 'pool': pool, 'admin_id': admin_id})
        apscheduler.add_job(apsched.send_message_cron, trigger='cron', hour=hour,
                        minute=minutes, start_date=datetime.now(), kwargs={'bot': bot, 'pool': pool, 'admin_id': admin_id})
        await call.message.answer(
            f'<b>Новое время рассылки установлено: {hour}:{minutes}</b> \U000023F0'
        )
        await call.answer()
    except:
        text = '<s>Ошибка при удалении домашних заданий</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def callback_del_homework_access(call: CallbackQuery, bot: Bot, callback_data: DeleteObj, request: Request):
    try:
        lessonId = callback_data.lessonId
        await request.clear_homeworks_from_lesson(lessonId)
        await request.clear_homeworksReserve_from_lesson(lessonId)
        await call.message.answer(
            f'<b>Домашние задания успешно удалены</b> \U00002705'
        )
        await call.answer()
    except:
        text = '<s>Ошибка при удалении домашних заданий</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def callback_del_lesson_access(call: CallbackQuery, bot: Bot, callback_data: DeleteObj, request: Request):
    try:
        lessonId = callback_data.lessonId
        await request.del_lesson_by_id(lessonId)
        if os.path.isfile(f'core/src/photo/lesson{lessonId}.jpg'):
            os.remove(f'core/src/photo/lesson{lessonId}.jpg')
        await call.message.answer(
            f'<b>Урок успешно удалён</b> \U00002705'
        )
        await call.answer()
    except:
        text = '<s>Ошибка при удалении урока</s>, если к данному уроку прикреплены домашние задания, то сначала нужно удалить их'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def callback_del_homework_cancel(call: CallbackQuery, bot: Bot):
    try:
        await call.message.answer(
            f'<b>Отменено</b> \U0000274C'
        )
        await call.answer()
    except:
        text = '<s>Ошибка</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def callback_del_lesson_cancel(call: CallbackQuery, bot: Bot):
    try:
        await call.message.answer(
            f'<b>Отменено</b> \U0000274C'
        )
        await call.answer()
    except:
        text = '<s>Ошибка</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def del_homework(call: CallbackQuery, bot: Bot, callback_data: LessonInfo):
    try:
        lessonId = callback_data.id
        await call.message.answer(
            f'<b>Подтвердите удаление</b> \U00002049',
            reply_markup=get_access_del(lessonId,'Homework')
        )
        await call.answer()
    except:
        text = '<s>Ошибка при удалении урока</s>, если к данному уроку прикреплены домашние задания, то сначала нужно удалить их'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def del_lesson(call: CallbackQuery, bot: Bot, callback_data: LessonInfo):
    try:
        lessonId = callback_data.id
        await call.message.answer(
            f'<b>Подтвердите удаление</b> \U00002049',
            reply_markup=get_access_del(lessonId,'Lesson')
        )
        await call.answer()
    except:
        text = '<s>Ошибка при удалении урока</s>, если к данному уроку прикреплены домашние задания, то сначала нужно удалить их'
        await bot.send_message(call.from_user.id, text)
        await call.answer()

async def callback_get_statistic(call: CallbackQuery, bot: Bot, request: Request):
    try:
        students = await request.get_all_students_isDone("yes")
        answerStr = ""
        isStat = True

        for student in students:
            answerStr += "\n\n"
            homeworks = await request.get_all_homeworks_by_studentId_isDone(student['tgid'], True)
            if student['firstname'] is not None:
                answerStr += student['firstname']
            else:
                answerStr += student['tgid']
            for homework in homeworks:
                isStat = False
                answerStr += "\n"
                titleLesson = await request.get_lesson_by_id(homework['lessonid'])
                if titleLesson[0] is not None:
                    answerStr += titleLesson[0]['title'] + " - "
                    if await request.check_homeworks_isDone(homework['lessonid'], student['tgid'], True):
                        answerStr += "Отлично!"
                        
        if isStat:
            answerStr = "Статистики пока нет \U0001F937"
        await call.message.answer(
            answerStr
        )
        await call.answer()
    except:
        text = '<s>Ошибка при вычислении статистики</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()
        
async def callback_get_statistic_lessons(call: CallbackQuery, bot: Bot, request: Request):
    try:
        all_lesson = await request.get_all_lesson()
        list_Lessons = [dict(row) for row in all_lesson]
        lessons = []
        for lesson in list_Lessons:
            newLesson = Lesson(lesson['id'], lesson['title'], lesson['description'], lesson['url'], lesson['datelesson'])
            lessons.append(newLesson)
        if len(lessons) > 0:
            await call.message.answer(
                f'<b>Выбери урок</b> статистику к которому ты ищешь) \U0001F4CA',
                reply_markup=get_inline_keyboard(lessons, 'statistic', call.from_user.id)
            )
        else:
            await call.message.answer(
                f'<b>Уроков нет</b> \U0001F937'
            )
        await call.answer()
    except:
        text = '<s>Ошибка при вычислении статистики</s>'
        await bot.send_message(call.from_user.id, text)
        await call.answer()
        
            
    

async def callback_add_lesson_access(call: CallbackQuery,  bot: Bot, callback_data: LessonInfo, request: Request):
    try:
        id = callback_data.id
        lessonReserve = await request.get_lessonReserve_by_id(id)
        lesson = await request.add_lesson(lessonReserve["title"], lessonReserve["description"], lessonReserve["url"], lessonReserve["datelesson"])
        if os.path.isfile(fr'D:\bot2\core\src\photo\newLesson.jpg'):
            if os.path.isfile(fr'D:\bot2\core\src\photo\lesson{lesson["id"]}.jpg'):
                os.remove(fr'D:\bot2\core\src\photo\lesson{lesson["id"]}.jpg')
            os.rename(fr'D:\bot2\core\src\photo\newLesson.jpg', fr'D:\bot2\core\src\photo\lesson{lesson["id"]}.jpg')
        await request.del_lessonReserve_by_id(id)
        await call.answer()
        await bot.send_message(call.from_user.id, "Урок успешно добавлен \U00002705")
    except:
        await call.answer()
        await bot.send_message(call.from_user.id, "<s>Ошибка при добавлении изображения</s>")

async def callback_add_lesson_cancel(call: CallbackQuery,  bot: Bot, callback_data: LessonInfo, request: Request):
    try:
        id = callback_data.id
        if os.path.isfile(f'core/src/photo/newLesson.jpg'):
            os.remove(f'core/src/photo/newLesson.jpg')
        await request.del_lessonReserve_by_id(id)
        await call.answer()
        await bot.send_message(call.from_user.id, "Отменено \U0000274C")
    except:
        await call.answer()
        await bot.send_message(call.from_user.id, "<s>Ошибка при отмене</s>")