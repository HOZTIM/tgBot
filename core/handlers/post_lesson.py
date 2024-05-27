from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.utils.dbconnect import Request
from core.utils.statesform import StepsForm
import re
from aiogram.types import FSInputFile
from core.keyboards.inline import get_access_add_lesson
from core.utils.lesson import Lesson

async def post_lesson_title(message: Message,  bot: Bot, state: FSMContext):
    try:
        title = message.text
        await state.update_data(title=title)
        await bot.send_message(message.from_user.id, "\U00000032 - Введите описание нового урока (не более одного сообщения) \U0001F9FE")
        await state.set_state(StepsForm.GET_LESSON_DESCRIPTION)
    except:
        await bot.send_message(message.from_user.id, "<s>Ошибка при добавлении заголовка</s>")
    
async def post_lesson_description(message: Message,  bot: Bot, state: FSMContext):
    try:
        description = message.text
        await state.update_data(description=description)
        await bot.send_message(message.from_user.id, "\U00000033 - Отправьте мне ссылку на урок \U0001F4CE")
        await state.set_state(StepsForm.GET_LESSON_URL)
    except:
        await bot.send_message(message.from_user.id, "<s>Ошибка при добавлении описания</s>")
    
async def post_lesson_url(message: Message,  bot: Bot, state: FSMContext):
    try:
        url = message.text
        await state.update_data(url=url)
        await bot.send_message(message.from_user.id, "\U00000034 - Теперь сформируем дату урока, отправьте год в формате yyyy \U0001F4C6 \n\nПример:\n2023")
        await state.set_state(StepsForm.GET_LESSON_YEAR)
    except:
        await bot.send_message(message.from_user.id, "<s>Ошибка при добавлении ссылки</s>")

async def post_lesson_year(message: Message,  bot: Bot, state: FSMContext):
    try:
        year = message.text
        result = re.match(r'^\d{4}$', year)
        if result != None:
            await state.update_data(year=year)
            await bot.send_message(message.from_user.id, "\U00000035 - Отправьте месяц в формате mm (от 1 до 12) \U0001F4C6 \n\nПример:\n05\n\nЕщё пример:\n5")
            await state.set_state(StepsForm.GET_LESSON_MONTH)
        else:
            await bot.send_message(message.from_user.id, "\U00000034 - Попробуйте еще раз, например отправьте четыре цифры без пробелов \U0001F4C6")
    except:
        await bot.send_message(message.from_user.id, "<s>Ошибка при добавлении года</s>")
    
async def post_lesson_month(message: Message,  bot: Bot, state: FSMContext):
    try:
        month = message.text
        if ((int(month) >= 1) and (int(month) <= 12)):
            await state.update_data(month=month)
            await bot.send_message(message.from_user.id, "\U00000036 - Отправьте день в формате dd (от 1 до 31) \U0001F4C6 \n\nПример:\n14\n\nЕщё пример:\n05\n\nЕщё пример:\n5")
            await state.set_state(StepsForm.GET_LESSON_DAY)
        else:
            await bot.send_message(message.from_user.id, "\U00000035 - Попробуйте еще раз, например отправьте число от 1 до 12 \U0001F4C6")
    except:
        await bot.send_message(message.from_user.id, "<s>Ошибка при добавлении месяца</s>")

async def post_lesson_day(message: Message,  bot: Bot, state: FSMContext):
    try:
        day = message.text
        if ((int(day) >= 1) and (int(day) <= 31)):
            await state.update_data(day=day)
            await bot.send_message(message.from_user.id, "\U00000037 - Отправьте промо-картинку для вашего урока в формате jpg \U0001F5BC")
            await state.set_state(StepsForm.GET_LESSON_IMG)
        else:
            await bot.send_message(message.from_user.id, "\U00000036 - Попробуйте еще раз, например отправьте число от 1 до 31 \U0001F4C6")
    except:
        await bot.send_message(message.from_user.id, "<s>Ошибка при добавлении дня</s>")
async def post_lesson_img(message: Message,  bot: Bot, state: FSMContext, request: Request):
    try:
        context_data = await state.get_data()
        title = context_data.get('title')
        description = context_data.get('description')
        url = context_data.get('url')
        year = context_data.get('year')
        month = context_data.get('month')
        day = context_data.get('day')
        date = year+'-'+month+'-'+day
        photoList = message.photo
        file_id = ''
        for photo in photoList:
            file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        destination = f'core/src/photo/newLesson.jpg'
        await bot.download_file(file_path, destination)

        answer = f'{title}\n \n{description}\n\nСсылка на урок: \n{url}\n \nДата урока: {date}'
        photo_mg = FSInputFile(fr'D:\bot2\core\src\photo\newLesson.jpg')
        await bot.send_photo(message.from_user.id, photo_mg, caption=answer)
        lessonData = Lesson(0, title, description, url, date)

        lessonReserve = await request.add_lessonReserve(title, description, url, date)
        await bot.send_message(
            message.from_user.id, 
            f'Подтверждение',
            reply_markup=get_access_add_lesson(lessonReserve["id"])
        )
    except:
        await bot.send_message(message.from_user.id, "\U00000037 - Отправьте промо-картинку для вашего урока в формате jpg \U0001F5BC")
