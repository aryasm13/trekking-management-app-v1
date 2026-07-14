from database.db import db
from database.models import User
from werkzeug.security import generate_password_hash

def create_admin():
    chk_adm=User.query.filter_by(role="admin").first()
    if chk_adm:
        return False
    new_adm = User(
        full_name = "System Administrator",
        email="admintrek@gmail.com",
        password_hash=generate_password_hash("Admin123"),
        role="admin",
        status="approved",
        contact_no="9876543210"
    )
    db.session.add(new_adm)
    db.session.commit()
    return True
