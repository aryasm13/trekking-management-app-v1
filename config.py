import os
bDir =os.path.abspath(os.path.dirname( __file__ ))
class Config:
    SECRET_KEY = "trekkey13"
    SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(bDir, "instance", "trek.db")
    SQLALCHEMY_TRACK_MODIFICATIONS=False
