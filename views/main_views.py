from flask import Blueprint, render_template, request, redirect, url_for
from dbModule import Database
import datetime, json, hashlib

bp = Blueprint('main', __name__, url_prefix='/')
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

        user_info = db.searchAccount(login_id, login_pw)
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

    db.addStudent(account_id, student_name, password, student_num, phone_num)

    return "회원가입 완료"


@bp.route('/equipments')
def equipments():
    sql = "SELECT * FROM equipments"
    equipments = db.executeAll(sql)
    return render_template('equipments.html', equipments=equipments)


@bp.route('/add_equipment', methods=['POST'])
def add_equipment():
    name = request.form['name']
    category = request.form['category']
    description = request.form['description']
    quantity = request.form['quantity']
    purchase_date = request.form['purchase_date']
    location = request.form['location']

    db.addEquipment(name, category, description, quantity, purchase_date, location)
    return redirect(url_for('main.equipments'))


@bp.route('/delete_equipment', methods=['POST'])
def delete_equipment():
    if request.method == 'POST':
        equipment_id = request.form['id'] 
        db.deleteEquipment(equipment_id)
        
        return redirect(url_for('main.equipments'))


@bp.route('/admin') # 사용자들의 정보를 모두 볼 수 있는 관리자 페이지
def admin():
    sql = "SELECT * FROM user"
    users = db.executeAll(sql)
    
    return render_template('admin.html', data=users)