from flask import Flask


def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///project_data.db'

    app.config['SECRET_KEY']='TESTOWE'
    app.config['SECURITY_REGISTERABLE']=True
    app.config['SECURITY_SEND_REGISTER_EMAIL']=False    
    
    with app.app_context():
        from . import routes
        from .models import db
        
        db.init_app(app)
        db.create_all()
        app.register_blueprint(routes.bp)

        
    return app