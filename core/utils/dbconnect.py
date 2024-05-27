import asyncpg


class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_payment(self, amount, tgId, status, paymentId):
        query = f"INSERT INTO Payment (amount, tgId, status, paymentId) VALUES ('{amount}','{tgId}','{status}', '{paymentId}')"
        await self.connector.execute(query)

    async def add_client(self, tgId, firstname):
        query = f"INSERT INTO Client (tgId, firstname) VALUES ('{tgId}', '{firstname}')"
        await self.connector.execute(query)

    async def check_status(self, tg_id, status):
        query = f"select * from Client join Payment on Client.tgId = Payment.tgId where Payment.status='{status}' and Payment.tgId = '{tg_id}'"
        return await self.connector.execute(query)
    
    async def get_all_students_isDone(self, status):
        query = f"select * from Client join Payment on Client.tgId = Payment.tgId where Payment.status='{status}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data
    
    async def check_status_user(self, tg_id):
        query = f"select Payment.status from Client join Payment on Client.tgId = Payment.tgId where Payment.tgId = '{tg_id}'"
        return await self.connector.fetch(query)

    async def get_status_client(self, tg_id):
        query = f"select Payment.status from Client join Payment on Client.tgId = Payment.tgId where Payment.tgId = '{tg_id}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        boolP = False
        for item in data:
            if(item['status'] == 'yes'):
                boolP = True
        return boolP
    
    async def check_id(self, tg_id):
        query = f"select * from Client where tgId = '{tg_id}'"
        return await self.connector.execute(query)

    async def update_status(self, paymentId, status):
        query = f"UPDATE Payment SET status='{status}' WHERE paymentId='{paymentId}'"
        await self.connector.execute(query)
    
    async def get_all_by_status(self, status):
        query = f"select tgId, paymentId from payment where status = '{status}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data
    
    async def get_today_lesson(self, date):
        query = f"select * from lesson where datelesson = '{date}'"
        return await self.connector.fetch(query)

    async def get_all_lesson(self):
        query = f"select * from lesson order by datelesson"
        return await self.connector.fetch(query)

    async def get_all_lesson_for_user(self, studentId):
        query = f"select lesson.id,  lesson.title, lesson.description, lesson.url, lesson.datelesson from lesson join homework on lesson.id = homework.lessonid where homework.isdone=True and homework.clientid = '{studentId}' order by lesson.datelesson "
        return await self.connector.fetch(query)

    async def get_first_lesson_for_user(self):
        query = f"select * from lesson where datelesson =  ( SELECT MIN(datelesson) FROM lesson)"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data
    
    async def get_next_lesson_for_user(self, studentId):
        query = f"select lesson.id,  lesson.title, lesson.description, lesson.url, lesson.datelesson from lesson join homework on lesson.id = homework.lessonid where homework.isdone=False and homework.clientid = '{studentId}' order by lesson.datelesson "
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        if len(data) > 0:
            return data[0]
        else:
            return False

    async def get_lesson_by_title(self, title):
        query = f"select * from lesson where title = '{title}'"
        return await self.connector.fetch(query)

    async def get_lesson_by_id(self, id):
        query = f"select * from lesson where id = '{id}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data

    async def get_lessonReserve_by_id(self, id):
        query = f"select * from lessonReserve where id = '{id}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data[0]

    async def get_count_students(self):
        query = f"select count(*) from Client join Payment on Client.tgId = Payment.tgId where Payment.status='yes'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        count = 0
        for item in data:
            count = item['count']
        return count
    
    async def get_count_students_lesson(self, lessonId, isDone):
        query = f"select count(*) from Client join Homework on Client.tgId = Homework.clientid where Homework.isdone='{isDone}' and Homework.lessonid='{lessonId}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        count = 0
        for item in data:
            count = item['count']
        return count


    async def add_homework(self, clientId, urlhomework, lessonId):
        query = f"INSERT INTO homework (clientId, urlhomeworks, lessonid) VALUES ('{clientId}','{urlhomework}','{lessonId}') ON CONFLICT (clientId, lessonid) DO UPDATE SET clientId = '{clientId}', urlhomeworks = '{urlhomework}', lessonid = '{lessonId}'"
        await self.connector.execute(query)

    async def send_homework(self, issend, studentId,homeworkId):
        query = f"UPDATE homework SET issend = '{issend}' WHERE id = {homeworkId} and clientid = '{studentId}'"
        await self.connector.execute(query)

    async def clear_homeworks_from_lesson(self, lessonId):
        query = f"DELETE FROM homework WHERE lessonid = '{lessonId}'"
        await self.connector.execute(query)

    async def clear_homeworksReserve_from_lesson(self, lessonId):
        query = f"DELETE FROM homeworkReserve WHERE lessonid = '{lessonId}'"
        await self.connector.execute(query)

    async def get_all_homeworks(self):
        query = f"select * from homework"
        return await self.connector.fetch(query)
    
    async def get_homeworks_by_lessonId(self, lessonId, isDone, isSend):
        query = f"select * from homework where lessonid = '{lessonId}' and isDone = {isDone} and issend = '{isSend}'"
        return await self.connector.fetch(query)
    
    
    async def get_homeworks_by_studentId(self, lessonId, studentId, isDone):
        query = f"select * from homework where lessonid = '{lessonId}' and clientid = '{studentId}' and isDone = {isDone}"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data
    
    async def get_all_homeworks_by_studentId_isDone(self, studentId, isDone):
        query = f"select * from homework where clientid = '{studentId}' and isDone = {isDone}"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data
    
    async def check_homeworks_isDone(self, lessonId, studentId, isDone):
        query = f"select * from homework where lessonid = '{lessonId}' and clientid = '{studentId}' and isDone = {isDone}"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        if len(data) > 0:
            return True
        else:
            return False
    
    async def get_studentName_by_id(self, studentId):
        query = f"select * from client where tgid = '{studentId}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        name = 'defaultName'
        for item in data:
            name = item['firstname']
        return name

    async def set_homework_isDone(self, isDone, homeworkId):
        query = f"UPDATE homework SET isdone = {isDone} WHERE id = {homeworkId}"
        await self.connector.execute(query)
    
    async def get_all_homework_by_studentId(self, studentId):
        query = f"select * from homework where clientId='{studentId}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data

    async def get_homeworks_isDone(self, lessonId, studentId):
        query = f"select * from homework where lessonid = '{lessonId}' and clientid = '{studentId}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        isDone = False
        for item in data:
            isDone = item['isdone']
        return isDone

    async def get_homeworks_by_id(self, id):
        query = f"select * from homework where id = '{id}'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        homeworkOnly = ''
        for homework in data:
            homeworkOnly = homework
        return homeworkOnly

    async def add_lesson(self, title, description, url, datelesson):
        # получать id: получить последний id в таблице
        query = f"INSERT INTO Lesson (title, description, url, datelesson) VALUES ('{title}','{description}','{url}', '{datelesson}') ON CONFLICT (datelesson) DO UPDATE SET title = '{title}', description = '{description}', url = '{url}', datelesson = '{datelesson}' RETURNING id"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        lesson = ''
        for lessonNew in data:
            lesson = lessonNew
        return lesson

    async def add_lessonReserve(self, title, description, url, datelesson):
        # получать id: получить последний id в таблице
        query = f"INSERT INTO LessonReserve (title, description, url, datelesson) VALUES ('{title}','{description}','{url}', '{datelesson}') ON CONFLICT (datelesson) DO UPDATE SET title = '{title}', description = '{description}', url = '{url}', datelesson = '{datelesson}' RETURNING id"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        lesson = ''
        for lessonNew in data:
            lesson = lessonNew
        return lesson
    async def get_lesson_issend(self, issend):
        # получать id: получить последний id в таблице
        query = f"select DISTINCT lesson.id from lesson join homework on lesson.id = homework.lessonid where homework.issend={issend}"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data

    async def del_lesson_by_id(self, lessonId):
        query = f"DELETE FROM homeworkreserve WHERE lessonid = '{lessonId}'"
        await self.connector.execute(query)
        query = f"DELETE FROM homework WHERE lessonid = '{lessonId}'"
        await self.connector.execute(query)
        query = f"DELETE FROM lesson WHERE id = '{lessonId}'"
        await self.connector.execute(query)

    async def del_lessonReserve_by_id(self, lessonId):
        query = f"DELETE FROM lessonReserve WHERE id = '{lessonId}'"
        await self.connector.execute(query)

    async def check_homework(self, clientid, lessonid):
        query = f"select * from homework where clientid = '{clientid}' and lessonid = '{lessonid}' "
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        if len(data) > 0:
            return False
        else:
            return True
        
    async def get_count_need_homework_for_lesson(self, lessonid):
        query = f"select * from homework where lessonid = '{lessonid}' "
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]

        query = f"select count(*) from Client join Payment on Client.tgId = Payment.tgId where Payment.status='yes'"
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        count = 0
        for item in data:
            count = item['count']
        
        return len(data) - int(count)

    async def add_homeworkReserve(self, clientId, urlhomework, lessonId):
        query = f"INSERT INTO homeworkReserve (clientId, urlhomeworks, lessonid) VALUES ('{clientId}','{urlhomework}','{lessonId}')"
        await self.connector.execute(query)
    
    async def get_homeworkReserve(self, lessonId):
        query = f"select * from homeworkReserve where lessonid = '{lessonId}' "
        res = await self.connector.fetch(query)
        data = [dict(row) for row in res]
        return data

    async def del_homeworkReserve(self, urlhomework, lessonId):
        query = f"DELETE FROM homeworkReserve WHERE lessonid = '{lessonId}' and urlhomeworks = '{urlhomework}' "
        await self.connector.execute(query)
