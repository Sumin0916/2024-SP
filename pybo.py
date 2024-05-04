import sys
sys.path.append('./views')

from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    import main_views
    app.register_blueprint(main_views.bp)

    return app