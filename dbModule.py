import pymysql

class Database():
    def __init__(self): 
        self.db = pymysql.connect(host='qbct6vwi8q648mrn.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
                            port=3306,
                            user='h8n2dnx48lgj0h1e',
                            passwd='lzwx5n8ibykmg9n4',
                            db='egwk7k1q8neh1ptw',
                            charset='utf8mb4',
                    )
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
    
    def execute(self, query, args={}):
        self.cursor.execute(query, args)

    def executeOne(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row
    
    def executeAll(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.db.commit()