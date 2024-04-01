import sys
sys.path.append('./views')

from flask import Flask

def create_app():
    app = Flask(__name__)
    
    import main_views
    app.register_blueprint(main_views.bp)

    return app