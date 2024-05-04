from flask import Blueprint, render_template, request, redirect, url_for, abort, session, flash
from dbModule import Database
# from WebStockServer.DBmodels import ArticleRepository
# import datetime, json, hashlib
# from time import time

bp = Blueprint('main', __name__, url_prefix='/')
db = Database()


@bp.route('/')
def main():
    user_info = session.get('user_info')
    return render_template('main.html', user_info=user_info)


@bp.route('/login_account', methods=['GET', 'POST'])
def login_account():
    if request.method == 'POST':
        data = request.form
        login_id = data['login_id']
        login_pw = data['login_pw']

        user_info = db.searchAccount(login_id, login_pw)
        if user_info:
            session['user_info'] = user_info
            return redirect('/')
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


@bp.route('/logout')
def logout():
    session.pop('user_info', None)
    return redirect('/')


@bp.route('/mypage')
def mypage():
    student_num = session.get('user_info').get('student_num')
    if student_num:
        sql = "SELECT * FROM user WHERE student_num = %s"
        user_info = db.executeOne(sql, (student_num))
        if user_info:
            return render_template('mypage.html', user_info=user_info)
        else:
            jsonify({"error": "해당 학번의 사용자가 존재하지 않습니다."}), 404
    else:
        jsonify({"error": "세션에 학번이 존재하지 않습니다."}), 404


@bp.route('/update_phone_number', methods=['POST'])
def update_phone_number():
    new_phone_number = request.form.get('phone_num')
    user_info = session.get('user_info')
    if user_info:
        student_num = user_info.get('student_num')
        sql = "UPDATE user SET phone_num = %s WHERE student_num = %s"
        db.executeOne(sql, (new_phone_number, student_num))
        db.commit()
        return redirect(url_for('main.mypage'))
    return jsonify({"error": "세션에 사용자 정보가 없습니다."}), 404


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
    user_info = session.get('user_info')
    sql = "SELECT * FROM board ORDER BY theme, num DESC"
    data_list = db.execute_board(sql)
    return render_template('notice_board.html', data_list=data_list, user_info=user_info)


@bp.route('/write')
def write():
    user_info = session.get('user_info')
    if user_info:
        return render_template('write_post.html')

    flash("로그인이 필요합니다.")
    return redirect(url_for('main.notice_board'))


@bp.route('/write_post', methods=['POST'])
def write_post():
    title = request.form['title']
    content = request.form['content']
    theme = request.form['theme']
    writer = session.get('user_info').get('account_id')
    
    db.newWrite(title, writer, content, theme)
    return redirect(url_for('main.notice_board'))
        


@bp.route('/delete_post', methods=['POST'])
def delete_post():
    post_id = request.form['num']
    writer = request.form['writer']
    user_info = session.get('user_info')
    user_id = user_info.get('account_id')
    if user_id in ('admin', writer):
        student_num = user_info.get('student_num')
        sql = "DELETE FROM board WHERE num = %s"
        db.executeOne(sql, (post_id))
        db.commit()
    else:
        flash("수정할 권한이 없습니다.")
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
