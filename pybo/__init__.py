from flask import Flask

def create_app():
    app = Flask(__name__)

    from .views import main_views
    app.register_blueprint(main_views.bp)
    #main_views.py 파일에 생성한 블루프린트 객체 bp를
    #app.register_blueprint(main_views.bp) 로 등록
    return app