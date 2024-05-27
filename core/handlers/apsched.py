from aiogram import Bot
from datetime import datetime
from core.utils.lesson import Lesson
from core.utils.pay import check_payment
from aiogram.types import FSInputFile

async def check_all_status(bot: Bot, pool, admin_id):
    query_get_all_by_status = f"select tgId, paymentId from payment where status = 'waiting'"

    async with pool.acquire() as con:
        res = await con.fetch(query_get_all_by_status)
        data = [dict(row) for row in res]
        for payment in data:
            try:
                payment_id = payment['paymentid']
                client_id = payment['tgid']
                if(await check_payment(payment['paymentid'])):
                    await con.execute(f"UPDATE Payment SET status='yes' WHERE paymentId='{payment_id}'")
                    await bot.send_message(admin_id, f'Пользователь <b>{client_id}</b> успешно оплатил курсы')
                else:
                    await con.execute(f"UPDATE Payment SET status='no' WHERE paymentId='{payment_id}'")
                    await bot.send_message(admin_id, f'Пользователь <b>{client_id}</b> пытался, но не оплатил курсы')
            except:
                await bot.send_message(admin_id, f'<s>Проверка платежа <b>{payment_id}</b> при запуске бота неудалась</s>')
    
async def send_message_cron(bot: Bot, pool, admin_id):
    dateToday = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day)
    students = [] 
    data = []
    query = f"select tgId, paymentId from payment where status = 'yes'"
    try:
        async with pool.acquire() as con:
            newLesson = Lesson()
            res = await con.fetch(query)
            data = [dict(row) for row in res]
            for payment in data:
                students.append(payment['tgid'])

            dateToday = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day)
            query_get_today_lesson = f"select * from lesson where datelesson = '{dateToday}'"
            res_lesson_today = await con.fetch(query_get_today_lesson)
            lessons = [dict(row) for row in res_lesson_today]
            if len(lessons):
                for lesson in lessons:
                    newLesson.id = lesson['id']
                    newLesson.title = lesson['title']
                    newLesson.description = lesson['description']
                    newLesson.url = lesson['url']
                    newLesson.datelesson = lesson['datelesson']

                photo_mg = FSInputFile(fr'D:\bot2\core\src\photo\lesson{str(newLesson.id)}.jpg')
                for id in students:
                    answer = f'{str(newLesson.title)}\n \n{str(newLesson.description)}\n\nСсылка на урок:\n {str(newLesson.url)}\n \nДата урока: {str(newLesson.datelesson)}'
                    await bot.send_photo(str(id), photo_mg, caption=answer)
                answer = f'Рассылка урока прошла успешно:\n{str(newLesson.title)}\n \n{str(newLesson.description)}\n\nСсылка на урок:\n {str(newLesson.url)}\n \nДата урока: {str(newLesson.datelesson)}'
                await bot.send_photo(admin_id, photo_mg, caption=answer)
            else:
                await bot.send_message(admin_id, f'Уроков запланированных на сегодня <b>не найдено</b>')
    except:
        await bot.send_message(admin_id, f'<s>При отправке нового урока произошла ошибка!</s>')
