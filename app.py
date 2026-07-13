import os
from flask import Flask
from config import Config
from database.db import db
from database.models import User
from database.admin_creation import create_admin

app=Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.instance_path,exist_ok=True)
db.init_app(app)

with app.app_context():
    db.create_all()
    create_admin()

if __name__=="__main__":
    app.run(debug=True)
