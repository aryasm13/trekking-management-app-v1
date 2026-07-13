from flask import Blueprint,render_template,redirect,url_for,flash,request
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from database.db import db
from database.models import User,StaffProfile

auth_bp = Blueprint("auth",__name__)

def redirect_by_role(u_obj):
    if u_obj.role=="admin":
        return redirect(url_for("admin.dashboard"))
    elif u_obj.role=="staff":
        return redirect(url_for("staff.dashboard"))
    else:
        return redirect(url_for("user.dashboard"))

@auth_bp.route("/logout",methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.","info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)
    return render_template("index.html")

@auth_bp.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method=="POST":
        n_val=request.form.get("full_name","").strip()
        mail_in=request.form.get("email","").strip().lower()
        pw1=request.form.get("password","")
        pw2=request.form.get("confirm_password","")
        phone_num=request.form.get("contact_no","").strip()
        r_val=request.form.get("role","trekker")

        err_list=[]
        if not n_val:
            err_list.append("Full name is required.")
        if not mail_in or not mail_in.endswith("@gmail.com"):
            err_list.append("A valid Gmail address is required.")

        if phone_num:
            cl_digits="".join(c for c in phone_num if c.isdigit())
            if len(cl_digits)!=10:
                err_list.append("Phone number must be a valid 10-digit number.")
        else:
            err_list.append("Phone number is required.")

        if not pw1:
            err_list.append("Password is required.")
        else:
            if len(pw1)<8:
                err_list.append("Password must be at least 8 characters long.")
            if not any(c.isupper() for c in pw1):
                err_list.append("Password must contain at least one uppercase letter.")
            if not any(c.islower() for c in pw1):
                err_list.append("Password must contain at least one lowercase letter.")
            if not any(c.isdigit() for c in pw1):
                err_list.append("Password must contain at least one numeric character.")

        if pw1!=pw2:
            err_list.append("Passwords do not match.")

        if r_val not in ("staff","trekker"):
            err_list.append("Invalid role.")

        if err_list:
            for e in err_list:
                flash(e,"danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=mail_in).first():
            flash("Email already registered.","danger")
            return render_template("auth/register.html")

        u_status="pending" if r_val=="staff" else "approved"
        new_u=User(
            full_name=n_val,email=mail_in,
            password_hash=generate_password_hash(pw1),
            contact_no=phone_num,role=r_val,status=u_status,
        )
        db.session.add(new_u)
        db.session.flush()

        if r_val=="staff":
            p_obj=StaffProfile(user_id=new_u.id)
            db.session.add(p_obj)

        db.session.commit()

        if r_val=="staff":
            flash("Registered successfully! Pending admin approval.","info")
        else:
            flash("Registered successfully! You can login now.","success")

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method=="POST":
        mail_val=request.form.get("email","").strip().lower()
        pw_val =request.form.get("password","")

        u_row=User.query.filter_by(email=mail_val).first()

        if not u_row or not check_password_hash(u_row.password_hash,pw_val):
            flash("Invalid email or password.","danger")
            return render_template("auth/login.html")

        if u_row.status=="blacklisted":
            flash("Your account has been suspended. Please contact the administrator.","danger")
            return render_template("auth/login.html")

        if u_row.role=="staff" and u_row.status=="pending":
            flash("Your staff account is pending admin approval. Please check back later.","warning")
            return render_template("auth/login.html")

        login_user(u_row)
        flash(f"Welcome back, {u_row.full_name}!","success")
        return redirect_by_role(u_row)

    return render_template("auth/login.html")
