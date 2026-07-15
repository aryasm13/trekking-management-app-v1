from datetime import datetime
from flask import Blueprint,render_template,redirect,url_for,flash,request
from flask_login import login_required,current_user
from database.db import db
from database.models import User,Trek,Booking
from utils.decorators import admin_required

admin_bp = Blueprint("admin",__name__,url_prefix="/admin")

def parse_trek_form_data( f , current_trek = None ):
    errs = []
    t_name = f.get("trek_name","").strip()
    loc=f.get("location","").strip()
    diff = f.get("difficulty","")
    desc=f.get("description","").strip()
    s_date=f.get("start_date","")
    e_date = f.get("end_date","")
    staff_id_val=f.get("assigned_staff_id") or None
    img= f.get("image_url","").strip()
    stat=f.get("status","Pending")

    if not t_name:
        errs.append("Trek name is required.")
    if not loc:
        errs.append("Location is required.")
    if diff not in ("Easy","Moderate","Hard"):
        errs.append("Difficulty must be Easy, Moderate, or Hard.")
    if stat not in ("Pending","Approved","Open","Closed","Ongoing","Completed"):
        errs.append("Invalid status value.")

    try:
        price_val=int(f.get("price",1000))
        if price_val < 0:
            errs.append("Price per head cannot be negative.")
    except ValueError:
        price_val=1000
        errs.append("Price must be a number.")

    try:
        dur=int(f.get("duration_days",0))
        if dur < 1:
            errs.append("Duration must be at least 1 day.")
    except ValueError:
        dur=0
        errs.append("Duration must be a number.")

    try:
        slots=int(f.get("total_slots",0))
        if slots < 1:
            errs.append("Total slots must be at least 1.")
    except ValueError:
        slots=0
        errs.append("Total slots must be a number.")

    d1=d2=None
    try:
        d1=datetime.strptime(s_date,"%Y-%m-%d").date()
        d2=datetime.strptime(e_date,"%Y-%m-%d").date()
        if d2 < d1:
            errs.append("End date cannot be before start date.")
    except ValueError:
        errs.append("Start and end dates are required (YYYY-MM-DD).")

    if errs:
        return None,errs

    s_id=int(staff_id_val) if staff_id_val else None

    if current_trek:
        booked = current_trek.total_slots - current_trek.available_slots
        current_trek.trek_name = t_name
        current_trek.location = loc
        current_trek.difficulty = diff
        current_trek.duration_days = dur
        current_trek.total_slots = slots
        current_trek.available_slots = max(0,slots-booked)
        current_trek.description = desc
        current_trek.start_date = d1
        current_trek.end_date = d2
        current_trek.assigned_staff_id = s_id
        current_trek.status = stat
        current_trek.image_path = img or None
        current_trek.price = price_val
        return current_trek, []
    else:
        new_t = Trek(
            trek_name=t_name,location=loc,
            difficulty=diff,duration_days=dur,
            total_slots=slots,available_slots=slots,
            description=desc,start_date=d1,end_date=d2,
            assigned_staff_id=s_id,status="Pending",
            image_path=img or None,price=price_val
        )
        return new_t, []

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_treks = Trek.query.count()
    total_users=User.query.filter_by(role="trekker").count()
    total_staff = User.query.filter_by(role="staff").count()
    pending_staff=User.query.filter_by(role="staff",status="pending").count()
    total_bookings = Booking.query.count()
    status_counts = {
        "Pending": Trek.query.filter_by(status="Pending").count(),
        "Approved": Trek.query.filter_by(status="Approved").count(),
        "Open": Trek.query.filter_by(status="Open").count(),
        "Closed": Trek.query.filter_by(status="Closed").count(),
        "Ongoing": Trek.query.filter_by(status="Ongoing").count(),
        "Completed": Trek.query.filter_by(status="Completed").count()
    }
    recent_b = Booking.query.order_by(Booking.booking_date.desc()).limit(8).all()
    recent_t=Trek.query.order_by(Trek.created_at.desc()).limit(6).all()
    return render_template("admin/dashboard.html",
        total_treks=total_treks,total_users=total_users,
        total_staff=total_staff,pending_staff=pending_staff,
        total_bookings=total_bookings,trek_status_counts=status_counts,
        recent_bookings=recent_b,recent_treks=recent_t)

@admin_bp.route("/bookings")
@login_required
@admin_required
def bookings():
    sf=request.args.get("status","")
    q=Booking.query
    if sf:
        q=q.filter_by(booking_status=sf)
    all_b=q.order_by(Booking.booking_date.desc()).all()
    return render_template("admin/bookings.html",bookings=all_b,status_filter=sf)

@admin_bp.route("/staff/<int:user_id>/approve",methods=["POST"])
@login_required
@admin_required
def staff_approve(user_id):
    u = User.query.get_or_404(user_id)
    if u.role != "staff":
        flash("Not staff.","danger")
        return redirect(url_for("admin.staff"))
    u.status = "approved"
    db.session.commit()
    flash(f"Staff {u.full_name} approved.","success")
    return redirect(url_for("admin.staff"))

@admin_bp.route("/user/<int:user_id>/blacklist",methods=["POST"])
@login_required
@admin_required
def user_blacklist(user_id):
    u = User.query.get_or_404(user_id)
    if u.role == "admin":
        flash("Cannot blacklist admin.","danger")
        return redirect(url_for("admin.users"))
    u.status="blacklisted"
    db.session.commit()
    flash(f"User {u.full_name} has been blacklisted.","warning")
    next_url=request.form.get("next",url_for("admin.users"))
    return redirect(next_url)

@admin_bp.route("/trek/<int:trek_id>/edit",methods=["GET","POST"])
@login_required
@admin_required
def trek_edit(trek_id):
    t=Trek.query.get_or_404(trek_id)
    staff_list=User.query.filter_by(role="staff",status="approved").all()
    if request.method == "POST":
        updated,errors = parse_trek_form_data(request.form,current_trek=t)
        if errors:
            for e in errors:
                flash(e,"danger")
            return render_template("admin/trek_form.html",trek=t,staff_list=staff_list,action="edit",form_data=request.form)
        db.session.commit()
        flash("Trek updated successfully!","success")
        return redirect(url_for("admin.treks"))
    return render_template("admin/trek_form.html",trek=t,staff_list=staff_list,action="edit",form_data={})

@admin_bp.route("/treks")
@login_required
@admin_required
def treks():
    status_filter=request.args.get("status","")
    q=Trek.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    all_t=q.order_by(Trek.created_at.desc()).all()
    staff_list=User.query.filter_by(role="staff",status="approved").all()
    return render_template("admin/treks.html",treks=all_t,staff_list=staff_list,status_filter=status_filter)

@admin_bp.route("/search")
@login_required
@admin_required
def search():
    query_str = request.args.get("q","").strip()
    stype=request.args.get("type","all")
    results = {"treks":[],"users":[],"staff":[]}

    if query_str:
        is_num = query_str.isdigit()
        if stype in ("all","trek"):
            base = Trek.query
            if is_num:
                results["treks"]=base.filter((Trek.trek_name.ilike(f"%{query_str}%"))|(Trek.id==int(query_str))).all()
            else:
                results["treks"]=base.filter(Trek.trek_name.ilike(f"%{query_str}%")|Trek.location.ilike(f"%{query_str}%")).all()

        if stype in ("all","user"):
            base=User.query.filter_by(role="trekker")
            if is_num:
                results["users"]=base.filter((User.full_name.ilike(f"%{query_str}%"))|(User.id==int(query_str))).all()
            else:
                results["users"]=base.filter(User.full_name.ilike(f"%{query_str}%")|User.email.ilike(f"%{query_str}%")).all()

        if stype in ("all","staff"):
            base=User.query.filter_by(role="staff")
            if is_num:
                results["staff"]=base.filter((User.full_name.ilike(f"%{query_str}%"))|(User.id==int(query_str))).all()
            else:
                results["staff"]=base.filter(User.full_name.ilike(f"%{query_str}%")|User.email.ilike(f"%{query_str}%")).all()

    return render_template("admin/search.html",results=results,query=query_str,search_type=stype)

@admin_bp.route("/staff/<int:user_id>/blacklist",methods=["POST"])
@login_required
@admin_required
def staff_blacklist(user_id):
    u = User.query.get_or_404(user_id)
    if u.role != "staff":
        flash("Not staff.","danger")
        return redirect(url_for("admin.staff"))
    u.status = "blacklisted"
    db.session.commit()
    flash(f"Staff {u.full_name} blacklisted.","warning")
    return redirect(url_for("admin.staff"))

@admin_bp.route("/trek/<int:trek_id>/delete",methods=["POST"])
@login_required
@admin_required
def trek_delete(trek_id):
    t=Trek.query.get_or_404(trek_id)
    db.session.delete(t)
    db.session.commit()
    flash("Trek deleted.","success")
    return redirect(url_for("admin.treks"))

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    sf=request.args.get("status","")
    q=User.query.filter_by(role="trekker")
    if sf:
        q=q.filter_by(status=sf)
    all_u=q.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html",users=all_u,status_filter=sf)

@admin_bp.route("/user/<int:user_id>/activate",methods=["POST"])
@login_required
@admin_required
def user_activate(user_id):
    u=User.query.get_or_404(user_id)
    u.status="approved"
    db.session.commit()
    flash(f"User {u.full_name} has been reactivated.","success")
    next_url=request.form.get("next",url_for("admin.users"))
    return redirect(next_url)

@admin_bp.route("/trek/new",methods=["GET","POST"])
@login_required
@admin_required
def trek_new():
    staff_list=User.query.filter_by(role="staff",status="approved").all()
    if request.method == "POST":
        trek,errors = parse_trek_form_data(request.form)
        if errors:
            for e in errors:
                flash(e,"danger")
            return render_template("admin/trek_form.html",staff_list=staff_list,action="new",form_data=request.form)
        db.session.add(trek)
        db.session.commit()
        flash("Trek created successfully!","success")
        return redirect(url_for("admin.treks"))
    return render_template("admin/trek_form.html",staff_list=staff_list,action="new",form_data={})

@admin_bp.route("/trek/<int:trek_id>/approve",methods=["POST"])
@login_required
@admin_required
def trek_approve(trek_id):
    t = Trek.query.get_or_404(trek_id)
    t.status = "Approved"
    db.session.commit()
    flash("Trek approved.","success")
    return redirect(url_for("admin.treks"))

@admin_bp.route("/staff")
@login_required
@admin_required
def staff():
    sf=request.args.get("status","")
    q=User.query.filter_by(role="staff")
    if sf:
        q=q.filter_by(status=sf)
    staff_list=q.order_by(User.created_at.desc()).all()
    return render_template("admin/staff.html",staff_list=staff_list,status_filter=sf)
