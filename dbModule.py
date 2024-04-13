import pymysql, hashlib

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
    
    def addStudent(self, account_id, name, pw, student_num, phone_num):
        sql = """
        INSERT INTO user (account_id, student_name, password_hash, student_num, phone_num)
        VALUES (%s, %s, %s, %s, %s)
        """
        hashed_pw = hashlib.sha256(pw.encode()).hexdigest()
        result_row = self.executeOne(sql, (account_id, name, hashed_pw, student_num, phone_num))
        self.commit()
        return result_row

    def searchAccount(self, login_id, login_pw):
        sql = "SELECT * FROM user WHERE account_id=%s AND password_hash=%s"
        hashed_pw = hashlib.sha256(login_pw.encode()).hexdigest()
        return self.executeOne(sql, (login_id, hashed_pw))

    def addEquipment(self, name="", category="", description="", quantity=0, purchase_date="", location=""):
        sql = """
        INSERT INTO equipments (name, category, description, quantity, purchase_date, location)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        result_row = self.executeOne(sql, (name, category, description, quantity, purchase_date, location))
        self.commit()
        return result_row

    def deleteEquipment(self, equipment_id):
        sql = "DELETE FROM equipments WHERE id = %s"
        result_row = self.executeOne(sql, (equipment_id))
        self.commit()
        return result_row

    def commit(self):
        self.db.commit()