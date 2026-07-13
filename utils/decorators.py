from functools import wraps
from flask import redirect,url_for, flash
from flask_login import current_user

def admin_required(   f):
    @wraps(f)
    def decorated( *args,**kwargs ):
        if not current_user.is_authenticated or current_user.role!="admin":
            flash("Admin access required.","danger")
            return redirect(url_for("auth.login"))
        return f( *args,**kwargs)
    return decorated

def staff_required(f ):
    @wraps( f)
    def decorated(*args,**kwargs):
        if not current_user.is_authenticated or current_user.role!="staff":
            flash("Staff access required.","danger")
            return redirect(url_for("auth.login"))
        if current_user.status!="approved":
            flash("Your staff account is pending approval.","warning")
            return redirect(url_for("auth.login"))
        return f(*args,**kwargs)
    return decorated

def trekker_required(f):
    @wraps(f)
    def decorated( *args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "trekker":
            flash("Trekker access required.","danger")
            return redirect(url_for("auth.login"))
        if current_user.status=="blacklisted":
            flash("Your account has been suspended.","danger")
            return redirect(url_for("auth.login"))
        return f(*args,**kwargs )
    return decorated
