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
    if request.path.startswith("/admin"):
        return User.query.filter_by(role="admin").first()
    elif request.path.startswith("/staff"):
        stf = User.query.filter_by(role="staff").first()
        if not stf:
            from werkzeug.security import generate_password_hash
            from database.models import StaffProfile
            stf = User(full_name="Test Staff", email="trekstaff@gmail.com", password_hash=generate_password_hash("staff123"), role="staff", status="approved", contact_no="8888888888")
            db.session.add(stf)
            db.session.flush()
            prof = StaffProfile(user_id=stf.id, emergency_contact="Emergency Contact", emergency_phone="1234567890", experience_years=3, specialization="Mountain Climbing", bio="Experienced trek leader.")
            db.session.add(prof)
            db.session.commit()
        return stf
    elif request.path.startswith("/user"):
        trk = User.query.filter_by(role="trekker").first()
        if not trk:
            from werkzeug.security import generate_password_hash
            trk = User(full_name="Test Trekker", email="trekker@gmail.com", password_hash=generate_password_hash("trekker123"), role="trekker", status="approved", contact_no="9999999999")
            db.session.add(trk)
            db.session.commit()
        return trk
    return User.query.filter_by(role="admin").first()

from routes.admin import admin_bp
from routes.user import user_bp
from routes.staff import staff_bp

app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(staff_bp)

with app.app_context():
    db.create_all()
    create_admin()

if __name__=="__main__":
    app.run(debug=True)
