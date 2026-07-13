from flask import Blueprint,render_template,redirect,url_for,flash,request
from flask_login import login_required,current_user
from database.db import db
from database.models import User,Trek,Booking,StaffProfile
from utils.decorators import staff_required

staff_bp=Blueprint("staff",__name__,url_prefix="/staff")

@staff_bp.route("/trek/<int:trek_id>/update",methods=["POST"])
@login_required
@staff_required
def trek_update(trek_id):
    t_obj = Trek.query.get_or_404(trek_id)
    if t_obj.assigned_staff_id != current_user.id:
        flash("You are not assigned to this trek.","danger")
        return redirect(url_for("staff.dashboard"))

    slot_val=request.form.get("available_slots","")
    st_val =request.form.get("status","")

    try:
        slots = int(slot_val)
        if slots < 0 or slots>t_obj.total_slots:
            flash(f"Slots must be between 0 and {t_obj.total_slots}.","danger")
            return redirect(url_for("staff.trek_detail",trek_id=trek_id))
    except ValueError:
        flash("Invalid slots number.","danger")
        return redirect(url_for("staff.trek_detail",trek_id=trek_id))

    ok_statuses = ["Open","Closed","Ongoing","Completed"]
    if st_val not in ok_statuses:
        flash("Invalid status.","danger")
        return redirect(url_for("staff.trek_detail",trek_id=trek_id))

    t_obj.available_slots=slots
    t_obj.status= st_val

    if st_val == "Completed":
        b_list = Booking.query.filter_by(trek_id=trek_id,booking_status="Booked").all()
        for b in b_list:
            b.booking_status = "Completed"

    db.session.commit()
    flash("Trek updated successfully!","success")
    return redirect(url_for("staff.trek_detail",trek_id=trek_id))

@staff_bp.route("/profile",methods=["GET","POST"])
@login_required
@staff_required
def profile():
    profile_obj=StaffProfile.query.filter_by(user_id=current_user.id).first()

    if request.method=="POST":
        f_name=request.form.get("full_name","").strip()
        tel=request.form.get("contact_no","").strip()
        emerg_contact=request.form.get("emergency_contact","").strip()
        emerg_ph =request.form.get("emergency_phone","").strip()
        exp_yr=request.form.get("experience_years","").strip()
        spec_area=request.form.get("specialization","").strip()
        bio_text=request.form.get("bio","").strip()

        if not f_name:
            flash("Full name is required.","danger")
            return render_template("staff/profile.html",profile=profile_obj)

        if tel:
            cl_digits1="".join(c for c in tel if c.isdigit())
            if len(cl_digits1) != 10:
                flash("Phone number must be a valid 10-digit number.","danger")
                return render_template("staff/profile.html",profile=profile_obj)
        else:
            flash("Phone number is required.","danger")
            return render_template("staff/profile.html",profile=profile_obj)

        if emerg_ph:
            cl_digits2 = "".join(c for c in emerg_ph if c.isdigit())
            if len(cl_digits2)!= 10:
                flash("Emergency contact phone must be 10 digits.","danger")
                return render_template("staff/profile.html",profile=profile_obj)

        current_user.full_name = f_name
        current_user.contact_no= tel

        if profile_obj:
            profile_obj.emergency_contact = emerg_contact or None
            profile_obj.emergency_phone= emerg_ph or None
            profile_obj.specialization = spec_area or None
            profile_obj.bio = bio_text or None
            try:
                profile_obj.experience_years = int(exp_yr) if exp_yr else None
            except ValueError:
                profile_obj.experience_years = None

        db.session.commit()
        flash("Profile updated successfully!","success")
        return redirect(url_for("staff.profile"))

    return render_template("staff/profile.html",profile=profile_obj)

@staff_bp.route("/dashboard")
@login_required
@staff_required
def dashboard():
    trek_list=Trek.query.filter_by(assigned_staff_id=current_user.id).order_by(Trek.start_date.asc()).all()
    stat_list =[]
    for tk in trek_list:
        bk_count=Booking.query.filter_by(trek_id=tk.id,booking_status="Booked").count()
        total_p = Booking.query.filter_by(trek_id=tk.id).count()
        stat_list.append({"trek":tk,"booked_count":bk_count,"total_participants":total_p})
    return render_template("staff/dashboard.html",trek_stats=stat_list)

@staff_bp.route("/trek/<int:trek_id>")
@login_required
@staff_required
def trek_detail(trek_id):
    t_obj=Trek.query.get_or_404(trek_id)
    if t_obj.assigned_staff_id != current_user.id:
        flash("You are not assigned to this trek.","danger")
        return redirect(url_for("staff.dashboard"))

    participants_list=Booking.query.filter_by(trek_id=trek_id).order_by(Booking.booking_date.asc()).all()
    booked_count= sum(1 for p in participants_list if p.booking_status == "Booked")

    return render_template("staff/trek_detail.html",trek=t_obj,participants=participants_list,booked_count=booked_count)
