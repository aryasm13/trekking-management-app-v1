from database.db import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id =db.Column(db.Integer, primary_key=True)
    full_name= db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash =db.Column(db.String(255), nullable=False)
    contact_no = db.Column(db.String(50), nullable=True)
    role =db.Column(db.Enum("admin", "staff", "trekker", name="user_roles", native_enum=False), nullable=False, default="trekker")
    status = db.Column(db.Enum("pending", "approved", "blacklisted", name="user_statuses", native_enum=False), nullable=False, default="approved")
    created_at =db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    staff_profile = db.relationship("StaffProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    bookings = db.relationship("Booking", back_populates="user", lazy=True, cascade="all, delete-orphan")
    assigned_treks = db.relationship("Trek", back_populates="assigned_staff", lazy=True)
    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role} status={self.status}>"

class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id =db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    emergency_contact =db.Column(db.String(120), nullable=True)
    emergency_phone = db.Column(db.String(50), nullable=True)
    experience_years= db.Column(db.Integer, nullable=True)
    specialization =db.Column(db.String(255), nullable=True)
    bio =db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at= db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    user = db.relationship("User", back_populates="staff_profile", uselist=False)
    def __repr__(self):
        return f"<StaffProfile id={self.id} user_id={self.user_id}>"

class Trek(db.Model):
    __tablename__ = "treks"
    id= db.Column(db.Integer, primary_key=True)
    trek_name =db.Column(db.String(255), nullable=False)
    location= db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.Enum("Easy", "Moderate", "Hard", name="trek_difficulties", native_enum=False), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    total_slots =db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date =db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status= db.Column(db.Enum("Pending", "Approved", "Open", "Closed", "Ongoing", "Completed", name="trek_statuses", native_enum=False), nullable=False, default="Pending")
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at =db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    image_path = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    assigned_staff =db.relationship("User", back_populates="assigned_treks")
    bookings = db.relationship("Booking", back_populates="trek", lazy=True, cascade="all, delete-orphan")
    __table_args__ = (
        db.CheckConstraint("available_slots >= 0"),
        db.CheckConstraint("total_slots >= 0"),
        db.CheckConstraint("available_slots <= total_slots"),
    )
    def __repr__(self):
        return f"<Trek id={self.id} trek_name={self.trek_name} status={self.status}>"

class Booking(db.Model):
    __tablename__ = "bookings"
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id =db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    remarks= db.Column(db.Text, nullable=True)
    booking_date= db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    payment_status =db.Column(db.Enum("Pending", "Paid", "Refunded", name="payment_statuses", native_enum=False), nullable=False, default="Pending")
    booking_status=db.Column(db.Enum("Booked", "Cancelled", "Completed", name="booking_statuses", native_enum=False), nullable=False, default="Booked")
    user =db.relationship("User", back_populates="bookings")
    trek =db.relationship("Trek", back_populates="bookings")
    def __repr__(self):
        return f"<Booking id={self.id} user_id={self.user_id} trek_id={self.trek_id} status={self.booking_status}>"
