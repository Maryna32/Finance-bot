# import mysql.connector


# class DatabaseRequests:
#     def __init__(self):
#         self.cnx = mysql.connector.connect(user='pythonuser', password='HFS#*3fdsJDS', host='151.115.32.54',
#                                            database='bot')
#         self.cursor = self.cnx.cursor()

#     def select(self, query):
#         self.cursor.execute(query)
#         return self.cursor.fetchall()

#     def insert(self, query, values):
#         self.cursor.execute(query, values)
#         self.cnx.commit()
#         return self.cursor.lastrowid

#     def update(self, query):
#         self.cursor.execute(query)
#         self.cnx.commit()

import aiomysql


class DatabaseRequests:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host='151.115.32.54',
            user='pythonuser',
            password='HFS#*3fdsJDS',
            db='bot'
        )

    async def close(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def select(self, query):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                return await cur.fetchall()

    async def insert(self, query, values):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                await conn.commit()
                return cur.lastrowid

    async def update(self, query):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                await conn.commit()

