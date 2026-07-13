import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from database.db import db
from database.models import User
from database.admin_creation import create_admin

app=Flask(__name__,template_folder="templates")
app.config.from_object(Config)
os.makedirs(app.instance_path,exist_ok=True)
db.init_app(app)

lm = LoginManager(app)
lm.login_view = "auth.login"

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@lm.request_loader
def dev_login_bypass(request):
    return User.query.get(1)

from routes.admin import admin_bp
app.register_blueprint(admin_bp)

with app.app_context():
    db.create_all()
    create_admin()

if __name__=="__main__":
    app.run(debug=True)
