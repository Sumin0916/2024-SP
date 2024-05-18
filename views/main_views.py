from flask import Blueprint, render_template, request, redirect, url_for, abort, session, flash, jsonify, Flask
from dbModule import Database
from datetime import datetime, timedelta


bp = Blueprint('main', __name__, url_prefix='/')
db = Database()


def get_time_slots():  # 하루 동안 사용 가능한 시간 슬롯
    return ["09:00~11:00", "11:00~13:00", "13:00~15:00", "15:00~17:00", "17:00~19:00"]


def get_available_slots(date, room):
    taken_slots = set([res['time_slot'] for res in db.fetch("SELECT time_slot FROM reservations WHERE date = %s AND room = %s", (date, room))])
    return taken_slots


def get_rooms():
    return ['세미나룸1', '세미나룸2']


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
    user_info = session.get('user_info')
    if not user_info:
        flash("로그인이 필요합니다.")
        return redirect(url_for('main.equipments'))
    name = request.form['name']
    category = request.form['category']
    description = request.form['description']
    quantity = request.form['quantity']
    purchase_date = request.form['purchase_date']
    location = request.form['location']
    db.addEquipment(name, category, description, quantity, purchase_date, location, user_info)
    return redirect(url_for('main.equipments'))


@bp.route('/delete_equipment', methods=['POST'])
def delete_equipment():
    user_info = session.get('user_info')
    if request.method == 'POST':
        equipment_id = request.form['id']
        db.minusEquipment(equipment_id)

        return redirect(url_for('main.equipments'))


@bp.route('/modify_equipment_minus', methods=['POST'])
def minus_equipment():
    user_info = session.get('user_info')
    if request.method == 'POST':
        equipment_id = request.form['id']
        db.minusEquipment(equipment_id, user_info)

        return redirect(url_for('main.equipments'))


@bp.route('/modify_equipment_plus', methods=['POST'])
def plus_equipment():
    user_info = session.get('user_info')
    if request.method == 'POST':
        equipment_id = request.form['id']
        db.plusEquipment(equipment_id, user_info)

        return redirect(url_for('main.equipments'))


@bp.route('/notice_board')
def notice_board():
    user_info = session.get('user_info')
    sql = "SELECT * FROM board ORDER BY theme, num DESC"
    data_list = db.execute_board(sql)
    for item in data_list:
        item['createdAt'] += timedelta(hours=9)
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


@bp.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if request.method == 'GET':
        sql = "SELECT * FROM board WHERE num = %s"
        article = db.executeOne(sql, (post_id))
        user_info = session.get('user_info')
        if user_info is None:
            return redirect(url_for('login'))
        if user_info.get('account_id') != article.get('writer'):
            flash("수정할 권한이 없습니다.")
            return redirect(url_for('main.notice_board'))  # 게시글 목록 페이지로 리디렉션
        return render_template('edit_post.html', article=article)
    else:
        title = request.form['title']
        content = request.form['content']
        theme = request.form['theme']
        writer = session.get('user_info').get('account_id')
        sql = """
        UPDATE board
        SET title = %s, content = %s, theme = %s, updatedAt = CURRENT_TIMESTAMP
        WHERE num = %s
        """
        db.execute(sql, (title, content, theme, post_id))
        db.commit()
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
    user_info = session.get('user_info')
    db.executeOne("UPDATE board SET views = views + 1 WHERE num = %s", (num,))  # 조회수 증가
    db.commit()
    sql = "SELECT * FROM board WHERE num = %s"
    article = db.executeOne(sql, num)
    if article:
        return render_template('view_post.html', article=article, user_info=user_info)
    else:
        abort(404)


@bp.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        date = request.form.get('date')
        time_slot = request.form.get('time_slot')
        room = request.form.get('room')
        if not date or not time_slot or not room:
            return render_template('reserve.html', error="Please select date, time slot, and room.", date=date,
                                   available_slots=get_time_slots(), rooms=get_rooms())

        existing = db.fetch("SELECT * FROM reservations WHERE date = %s AND time_slot = %s AND room = %s",
                            (date, time_slot, room))
        if existing:
            error = "이미 예약된 시간대입니다. 다른 시간 또는 다른 세미나실을 선택해 주세요."
            taken_slots = get_available_slots(date, room)
            return render_template('reserve.html', error=error, date=date, available_slots=get_time_slots(),
                                   taken_slots=taken_slots, rooms=get_rooms(), selected_room=room)

        db.execute("INSERT INTO reservations (date, time_slot, room) VALUES (%s, %s, %s)", (date, time_slot, room))
        flash("예약이 완료되었습니다.")
        return redirect(url_for('main.reserve_view'))
    else:
        date = request.args.get('date', str(datetime.today().strftime('%Y-%m-%d')))
        room = request.args.get('room', 'room1')  #default
        taken_slots = get_available_slots(date, room)
        return render_template('reserve.html', date=date, available_slots=get_time_slots(),
                               taken_slots=taken_slots, rooms=get_rooms(), selected_room=room)


@bp.route('/add_reservation', methods=['POST'])
def add_reservation():
    data = request.get_json()
    date = data['date']
    time_slot = data['time_slot']
    db.execute("INSERT INTO reservations (date, time_slot) VALUES (%s, %s)", (date, time_slot))
    return jsonify({"status": "success", "message": "성공적으로 예약되었습니다!"})


@bp.route('/reserve_view')
def reserve_view():
    # message = request.args.get('message', '')
    sql = "SELECT * FROM reservations ORDER BY date, time_slot"
    reservations = db.fetch(sql)
    return render_template('reserve_view.html', reservations=reservations)


@bp.route('/get-reservations')
def get_reservations():
    # sql1 = "SELECT * FROM reservations ORDER BY date, time_slot"
    sql2 = "SELECT date, time_slot, room FROM reservations"
    reservations = db.fetch(sql2)
    events = []
    # FullCalendar의 이벤트 형식에 맞춰 데이터 변환
    for reservation in reservations:
        start_time, end_time = reservation['time_slot'].split('~')
        start_datetime = f"{reservation['date']}T{start_time}"
        end_datetime = f"{reservation['date']}T{end_time}"
        room_color = {
            '세미나룸1': '#007bff',
            '세미나룸2': '#28a745',
            # 'room3': '#ffc107'
        }
        events.append({
            'title': f"{reservation['time_slot']} 예약 ({reservation['room']})",
            'start': start_datetime,
            'end': end_datetime,
            'color': room_color.get(reservation['room'], '#333')
        })
    return jsonify(events)  # JSON 형식으로 이벤트 데이터 반환


@bp.route('/admin')  # 사용자들의 정보를 모두 볼 수 있는 관리자 페이지
def admin():
    sql = "SELECT * FROM user"
    users = db.executeAll(sql)

    return render_template('admin.html', data=users)


@bp.route('/404')
def not_found():
    abort(404)

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
