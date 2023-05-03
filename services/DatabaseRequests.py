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

