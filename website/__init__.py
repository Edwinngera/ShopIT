from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from .config  import Config
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


db=SQLAlchemy()


def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    migrate = Migrate(app, db)

    from .views import views
    from .auth import auth

    from .models import User,Product,Category,ProductCategory

    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # admin = Admin(app, name='Ecommerce Admin', template_mode='bootstrap3')
    # admin.add_view(ModelView(Product, db.session))
    # admin.add_view(ModelView(User, db.session))
    # admin.add_view(ModelView(Category, db.session))
    # admin.add_view(ModelView(ProductCategory, db.session))

    @login_manager.user_loader
    def load_user(userid):
        """Check if user is logged-in on every page load."""
        if userid is not None:
            return User.query.get(userid)
        return None
    
    return app





    