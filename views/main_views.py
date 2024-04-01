from flask import Blueprint, render_template

bp=Blueprint('main', __name__, url_prefix='/')

@bp.route('/hello')
def hello_pybo():
    return 'Hello, Pybo!'

@bp.route('/')
def main():
    return render_template('main.html')

@bp.route('/login_account')
def login_account():
    return render_template('login_account.html')

@bp.route('/home')
def home():
    return render_template('home.html')
