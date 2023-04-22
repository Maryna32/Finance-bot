import mysql.connector


class DatabaseRequests:
    def __init__(self):
        self.cnx = mysql.connector.connect(user='pythonuser', password='HFS#*3fdsJDS', host='151.115.32.54',
                                           database='bot')
        self.cursor = self.cnx.cursor()

    def select(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def insert(self, query, values):
        self.cursor.execute(query, values)
        self.cnx.commit()
        return self.cursor.lastrowid

    def update(self, query):
        self.cursor.execute(query)
        self.cnx.commit()