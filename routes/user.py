from flask import Blueprint,render_template,redirect,url_for,flash,request
from flask_login import login_required,current_user
from database.db import db
from database.models import User,Trek,Booking
from utils.decorators import trekker_required

user_bp=Blueprint("user",__name__,url_prefix="/user")

@user_bp.route("/bookings")
@login_required
@trekker_required
def bookings():
    b_list = Booking.query.filter_by(user_id=current_user.id, booking_status="Booked").order_by(Booking.booking_date.desc()).all()
    return render_template("user/bookings.html", bookings = b_list)

@user_bp.route("/trek/<int:trek_id>/book",methods=["POST"])
@login_required
@trekker_required
def book_trek(trek_id):
    t_obj =Trek.query.get_or_404(trek_id)
    if t_obj.status!="Open":
        flash("This trek is not open for bookings.","danger")
        return redirect(url_for("user.trek_detail",trek_id=trek_id))
    if t_obj.available_slots <= 0:
        flash("Sorry, no slots available.","danger")
        return redirect(url_for("user.trek_detail",trek_id=trek_id))
    exist_bk= Booking.query.filter_by(user_id=current_user.id,trek_id=trek_id,booking_status="Booked").first()
    if exist_bk:
        flash("You already booked this trek.","warning")
        return redirect(url_for("user.bookings"))
    
    new_bk = Booking(
        user_id =current_user.id, trek_id=trek_id,
        booking_status ="Booked", payment_status="Pending",
        remarks=request.form.get("remarks","").strip() or None
    )
    t_obj.available_slots -= 1
    db.session.add(new_bk)
    db.session.commit()
    flash("Successfully booked trek!","success")
    return redirect(url_for("user.bookings"))

@user_bp.route("/profile",methods=["GET","POST"])
@login_required
@trekker_required
def profile():
    if request.method =="POST":
        f_name = request.form.get("full_name","").strip()
        ph_num=request.form.get("contact_no","").strip()
        if not f_name:
            flash("Full name is required.","danger")
            return render_template("user/profile.html")
        if ph_num:
            clean_digits= "".join(c for c in ph_num if c.isdigit())
            if len(clean_digits) != 10:
                flash("Phone number must be a valid 10-digit number.","danger")
                return render_template("user/profile.html")
        current_user.full_name = f_name
        current_user.contact_no= ph_num
        db.session.commit()
        flash("Profile updated successfully!","success")
        return redirect(url_for("user.profile"))
    
    tot_bk = Booking.query.filter_by(user_id=current_user.id).count()
    done_bk = Booking.query.filter_by(user_id=current_user.id,booking_status="Completed").count()
    return render_template("user/profile.html",total_treks=tot_bk,completed_treks=done_bk)

@user_bp.route("/treks")
@login_required
@trekker_required
def treks():
    diff_val = request.args.get("difficulty","")
    loc_val=request.args.get("location","").strip()
    srch = request.args.get("search","").strip()
    
    q_obj = Trek.query.filter_by(status="Open")
    if diff_val in ("Easy","Moderate","Hard"):
        q_obj=q_obj.filter_by(difficulty=diff_val)
    if loc_val:
        q_obj =q_obj.filter(Trek.location.ilike(f"%{loc_val}%"))
    if srch:
        q_obj= q_obj.filter(Trek.trek_name.ilike(f"%{srch}%"))
        
    all_treks = q_obj.order_by(Trek.start_date.asc()).all()
    booked_ids = {b.trek_id for b in Booking.query.filter_by(user_id=current_user.id, booking_status="Booked").all()}
    return render_template("user/treks.html", treks=all_treks, booked_trek_ids=booked_ids, difficulty=diff_val, location=loc_val, search=srch)

@user_bp.route("/history")
@login_required
@trekker_required
def history():
    past_bk = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.booking_status.in_(["Completed","Cancelled"])
    ).order_by(Booking.booking_date.desc()).all()
    return render_template("user/history.html", history=past_bk)

@user_bp.route("/dashboard")
@login_required
@trekker_required
def dashboard():
    open_t = Trek.query.filter_by(status="Open").order_by(Trek.start_date.asc()).limit(6).all()
    active_bk = Booking.query.filter_by(user_id=current_user.id, booking_status="Booked").order_by(Booking.booking_date.desc()).all()
    past_bk = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.booking_status.in_(["Completed","Cancelled"])
    ).order_by(Booking.booking_date.desc()).limit(4).all()
    
    cnt_bk = Booking.query.filter_by(user_id=current_user.id, booking_status="Booked").count()
    cnt_done = Booking.query.filter_by(user_id=current_user.id, booking_status="Completed").count()
    cnt_cancel = Booking.query.filter_by(user_id=current_user.id, booking_status="Cancelled").count()
    return render_template("user/dashboard.html",
        open_treks=open_t, my_active_bookings=active_bk,
        recent_history=past_bk, booked_count=cnt_bk,
        completed_count=cnt_done, cancelled_count=cnt_cancel)

@user_bp.route("/booking/<int:booking_id>/cancel",methods=["POST"])
@login_required
@trekker_required
def cancel_booking(booking_id):
    bk_obj = Booking.query.get_or_404(booking_id)
    if bk_obj.user_id != current_user.id:
        flash("Unauthorized.","danger")
        return redirect(url_for("user.bookings"))
    if bk_obj.booking_status != "Booked":
        flash("Only active bookings can be cancelled.","danger")
        return redirect(url_for("user.bookings"))
    if bk_obj.trek.status == "Completed":
        flash("Cannot cancel a completed trek.","danger")
        return redirect(url_for("user.bookings"))
        
    bk_obj.booking_status = "Cancelled"
    bk_obj.trek.available_slots += 1
    db.session.commit()
    flash("Booking cancelled.","info")
    return redirect(url_for("user.bookings"))

@user_bp.route("/trek/<int:trek_id>")
@login_required
@trekker_required
def trek_detail(trek_id):
    t_obj = Trek.query.get_or_404(trek_id)
    eb_obj = Booking.query.filter_by(user_id=current_user.id, trek_id=trek_id, booking_status="Booked").first()
    return render_template("user/trek_detail.html", trek=t_obj, existing_booking=eb_obj)
