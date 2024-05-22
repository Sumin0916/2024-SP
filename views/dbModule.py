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
        self.db.commit()

    def executeOne(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row
    
    def executeAll(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row
    
    def addStudent(self, account_id, name, pw, student_num, phone_num):
        sql = "SELECT * FROM user WHERE account_id=%s"
        result_row = self.executeOne(sql, (account_id))
        if result_row:
            return False
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

    def addEquipment(self, name="", category="", description="", quantity=0, purchase_date="", location="", user_info=""):
        sql = """
        INSERT INTO equipments (name, category, description, quantity, purchase_date, location, latest_name , latest_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        latest_number = user_info.get('student_num')
        latest_name = user_info.get('student_name')
        result_row = self.executeOne(sql, (name, category, description, quantity, purchase_date, location, latest_name, latest_number))
        self.commit()
        return result_row

    def deleteEquipment(self, equipment_id, user_info):
        sql = "SELECT * FROM equipments WHERE id = %s"
        result_row = self.executeOne(sql, equipment_id)
        self.commit()
        student_name = user_info.get('student_name')
        if (student_name not in result_row) and student_name != 'admin':
            return 1
        sql = "DELETE FROM equipments WHERE id = %s"
        result_row = self.executeOne(sql, equipment_id)
        self.commit()
        return 0

    def minusEquipment(self, equipment_id, user_info):
        sql = "UPDATE equipments SET quantity = quantity -1, latest_name = %s, latest_number = %s WHERE id = %s"
        result_row = self.executeOne(sql,(user_info['student_name'], user_info['student_num'], equipment_id))
        self.commit()
        return result_row

    def plusEquipment(self, equipment_id, user_info):
        sql = "UPDATE equipments SET quantity = quantity +1, latest_name = %s, latest_number = %s WHERE id = %s"
        result_row = self.executeOne(sql,(user_info['student_name'], user_info['student_num'], equipment_id))
        self.commit()
        return result_row

    def execute_board(self, query, args={}):
        self.cursor.execute(query, args)
        data_list = self.cursor.fetchall()
        return data_list

    def newWrite(self, title="", writer="", content="", theme=""):
        sql = "INSERT INTO board (title, writer, content, views, theme) VALUES (%s, %s, %s, 0, %s)"
        values = (title, writer, content, theme)
        k = self.cursor.execute(sql, values)
        self.commit()
        return k

    def delWrite(self, write_id):
        sql = "DELETE FROM board WHERE id = %s"
        d = self.executeOne(sql, write_id)
        self.commit()
        return d

    def fetch(self, query, args={}):
        self.cursor.execute(query, args)
        return self.cursor.fetchall()

    def find(self, query, title):
        d = self.executeOne(query, title)
        return d

    def commit(self):
        self.db.commit()