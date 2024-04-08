from flask import Blueprint, render_template, request
from dbModule import Database
import datetime, json, hashlib

bp=Blueprint('main', __name__, url_prefix='/')
db = Database()


@bp.route('/')
def main():
    return render_template('main.html')


@bp.route('/login_account', methods=['GET', 'POST'])
def login_account():
    if request.method == 'POST':
        data = request.form
        login_id = data['login_id']
        login_pw = data['login_pw']
        hashed_login_pw = hashlib.sha256(login_pw.encode()).hexdigest()

        sql = "SELECT * FROM user WHERE account_id=%s AND password_hash=%s"
        user_info = db.executeOne(sql, (login_id, hashed_login_pw))

        if user_info:
            return f"로그인 완료. 사용자 정보: {user_info}"
        else:
            return "로그인 실패. 아이디 또는 비밀번호를 확인하세요."
    
    return render_template('login_account.html')


@bp.route('/home')
def home():
    return render_template('home.html')


@bp.route('/register', methods=['POST'])
def register():
    recieved_data = request.form
    student_num = recieved_data['regi_sn']
    student_name = recieved_data['regi_name']
    phone_num = recieved_data['regi_pn']
    password = recieved_data['regi_pw']
    account_id = recieved_data['regi_id']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    sql_query = """
    INSERT INTO user (account_id, student_name, password_hash, student_num, phone_num)
    VALUES (%s, %s, %s, %s, %s)
    """
    db.executeOne(sql_query, (account_id, student_name, hashed_password, student_num, phone_num))
    db.commit()
    return "회원가입 완료"


@bp.route('/admin') # 사용자들의 정보를 모두 볼 수 있는 관리자 페이지
def admin():
    sql = "SELECT * FROM user"
    users = db.executeAll(sql)
    
    return render_template('admin.html', data=users)