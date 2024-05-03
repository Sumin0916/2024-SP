from flask import Blueprint, render_template, request, redirect, url_for, abort
from dbModule import Database
# from WebStockServer.DBmodels import ArticleRepository
# import datetime, json, hashlib
# from time import time

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

@bp.route('/facility')
def facility():
    return render_template('facility.html')

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


@bp.route('/notice_board')
def notice_board():
    sql = "SELECT * FROM board ORDER BY num DESC"
    data_list = db.execute_board(sql)
    return render_template('notice_board.html', data_list=data_list)


@bp.route('/write')
def write():
    return render_template('write_post.html')


@bp.route('/write_post', methods=['POST'])
def write_post():
    title = request.form['title']
    writer = request.form['writer']
    content = request.form['content']
    theme = request.form['theme']
    db.newWrite(title, writer, content, theme)
    return redirect(url_for('main.notice_board'))


@bp.route('/notice_board/<int:num>/')
def view_post(num):
    db.executeOne("UPDATE board SET views = views + 1 WHERE num = %s", (num,)) #조회수 증가
    db.commit()
    sql = "SELECT * FROM board WHERE num = %s"
    article = db.executeOne(sql, num)
    if article:
        return render_template('view_post.html', article=article)
    else:
        abort(404)


@bp.route('/delete_post', methods=['POST'])
def delete_post():
    pass


# @bp.app_template_filter("formatdatetime")
# def format_datetime(value):
#     if value is None:
#         return ""
#     now_timestamp = time.time()
#     offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
#     value = datetime.fromtimestamp(int(value / 1000)) + offset
#     return value.strftime('%Y-%m-%d %H:%M:%S')


@bp.route('/admin') # 사용자들의 정보를 모두 볼 수 있는 관리자 페이지
def admin():
    sql = "SELECT * FROM user"
    users = db.executeAll(sql)
    
    return render_template('admin.html', data=users)

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
