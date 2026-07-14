import os
from datetime import datetime
from app import app
from database.db import db
from database.models import User,Trek,Booking,StaffProfile
from werkzeug.security import generate_password_hash

def run_seeder():
    with app.app_context():
        Booking.query.delete()
        Trek.query.delete()
        StaffProfile.query.delete()
        User.query.filter(User.role != "admin").delete()
        db.session.commit()

        adm_user=User.query.filter_by(role="admin").first()
        if adm_user:
            adm_user.password_hash=generate_password_hash("Admin123")
            adm_user.email="admintrek@gmail.com"
        else:
            adm_user=User(
                full_name="System Administrator",
                email="admintrek@gmail.com",
                password_hash=generate_password_hash("Admin123"),
                role="admin",
                status="approved",
                contact_no="9876543210"
            )
            db.session.add(adm_user)
        db.session.commit()

        # 22 Trekkers
        trekkers_data = [
            ("Amit Sharma", "amit.sharma@gmail.com", "9988776655"),
            ("Priya Patel", "priya.patel@gmail.com", "9876543210"),
            ("Rahul Verma", "rahul.verma@gmail.com", "8877665544"),
            ("Sneha Reddy", "sneha.reddy@gmail.com", "7766554433"),
            ("Abhishek Singh", "abhishek.singh@gmail.com", "9911223344"),
            ("Divya Nair", "divya.nair@gmail.com", "9822334455"),
            ("Karan Johar", "karan.johar@gmail.com", "9733445566"),
            ("Pooja Hegde", "pooja.hegde@gmail.com", "9644556677"),
            ("Siddharth Roy", "siddharth.roy@gmail.com", "9555667788"),
            ("Kriti Sanon", "kriti.sanon@gmail.com", "9466778899"),
            ("Varun Dhawan", "varun.dhawan@gmail.com", "9377889900"),
            ("Alia Bhatt", "alia.bhatt@gmail.com", "9288990011"),
            ("Ranbir Kapoor", "ranbir.kapoor@gmail.com", "9199001122"),
            ("Deepika Padukone", "deepika.padukone@gmail.com", "9088776655"),
            ("Ranveer Singh", "ranveer.singh@gmail.com", "8977665544"),
            ("Anushka Sharma", "anushka.sharma@gmail.com", "8866554433"),
            ("Virat Kohli", "virat.kohli@gmail.com", "8755443322"),
            ("Rohit Sharma", "rohit.sharma@gmail.com", "8644332211"),
            ("Hardik Pandya", "hardik.pandya@gmail.com", "8533221100"),
            ("Jasprit Bumrah", "jasprit.bumrah@gmail.com", "8422110099"),
            ("Rishabh Pant", "rishabh.pant@gmail.com", "8311009988"),
            ("Shreyas Iyer", "shreyas.iyer@gmail.com", "8200998877")
        ]

        t_objects = []
        for name, email, phone in trekkers_data:
            u_obj = User(
                full_name=name, email=email,
                password_hash=generate_password_hash("Trekker123"),
                contact_no=phone, role="trekker", status="approved"
            )
            db.session.add(u_obj)
            t_objects.append(u_obj)
        db.session.flush()

        # 6 Staff members
        staff_data = [
            ("Rohan Joshi", "rohan.joshi@gmail.com", "9900887766", "approved", 5, "High Altitude Rescue", "Himalayan guide with 5 years experience.", "Sunita Joshi", "9876543211"),
            ("Neha Gupta", "neha.gupta@gmail.com", "9800776655", "approved", 3, "Flora and Fauna hikes", "Nature enthusiast and rescue expert.", "Alok Gupta", "9876543212"),
            ("Vikram Singh", "vikram.singh@gmail.com", "9700665544", "approved", 4, "Glacier Trekking", "Passionate glacier explorer.", "Raj Singh", "9876543213"),
            ("Anjali Desai", "anjali.desai@gmail.com", "9600554433", "approved", 2, "Sahyadri Forts Navigation", "Expert in Sahyadri terrain.", "Mahesh Desai", "9876543214"),
            ("Rahul Bose", "rahul.bose@gmail.com", "9500443322", "approved", 6, "Rock Climbing & Rappelling", "Certified mountaineering instructor.", "Komal Bose", "9876543215"),
            ("Sandeep Patil", "sandeep.patil@gmail.com", "9400332211", "pending", 1, "Trek Lead Trainee", "Trainee guide.", "Sujata Patil", "9876543216"),
            ("Deepak Kumar", "deepak.kumar@gmail.com", "9300221100", "blacklisted", 7, "Advanced Survival", "Banned guide.", "Asha Kumar", "9876543217")
        ]

        s_objects = {}
        for s_info in staff_data:
            s_user = User(
                full_name=s_info[0], email=s_info[1],
                password_hash=generate_password_hash("Staff123"),
                contact_no=s_info[2], role="staff", status=s_info[3]
            )
            db.session.add(s_user)
            db.session.flush()
            s_objects[s_info[0]] = s_user

            prof = StaffProfile(
                user_id=s_user.id, emergency_contact=s_info[7],
                emergency_phone=s_info[8], experience_years=s_info[4],
                specialization=s_info[5], bio=s_info[6]
            )
            db.session.add(prof)
        db.session.commit()

        # 10 Treks
        tk1=Trek(
            trek_name="Kedarkantha Winter Trek",location="Uttarakhand",
            difficulty="Moderate",duration_days=6,total_slots=15,
            available_slots= 11,description="Beautiful winter trek in Uttarakhand.",
            start_date= datetime.strptime("2026-12-10","%Y-%m-%d").date(),
            end_date=datetime.strptime("2026-12-16","%Y-%m-%d").date(),
            status="Open",assigned_staff_id=s_objects["Rohan Joshi"].id
        )
        tk2 = Trek(
            trek_name= "Valley of Flowers", location="Himalayas, India",
            difficulty="Easy",duration_days=5,total_slots= 20,
            available_slots=17,description="World heritage site alpine flowers meadow.",
            start_date=datetime.strptime("2026-07-01","%Y-%m-%d").date(),
            end_date= datetime.strptime("2026-07-06","%Y-%m-%d").date(),
            status="Completed",assigned_staff_id=s_objects["Neha Gupta"].id
        )
        tk3=Trek(
            trek_name="Hampta Pass Trek",location="Himachal Pradesh",
            difficulty="Hard",duration_days=6,total_slots=12,
            available_slots=10,description="Dramatic crossover trek from Kullu valley to Spiti.",
            start_date=datetime.strptime("2026-07-10","%Y-%m-%d").date(),
            end_date=datetime.strptime("2026-07-16","%Y-%m-%d").date(),
            status="Ongoing",assigned_staff_id=s_objects["Rohan Joshi"].id
        )
        tk4=Trek(
            trek_name="Beas Kund Hike",location="Manali",
            difficulty="Easy",duration_days=3,total_slots=10,
            available_slots= 10,description="Short trek to source of Beas river.",
            start_date=datetime.strptime("2026-09-05","%Y-%m-%d").date(),
            end_date=datetime.strptime("2026-09-08","%Y-%m-%d").date(),
            status="Approved",assigned_staff_id=s_objects["Neha Gupta"].id
        )
        tk5 = Trek(
            trek_name="Roopkund Trek Mystery",location="Garhwal Himalayas",
            difficulty="Hard",duration_days=8,total_slots=8,
            available_slots=8,description="High altitude glacial lake trek.",
            start_date=datetime.strptime("2026-10-01","%Y-%m-%d").date(),
            end_date=datetime.strptime("2026-10-08","%Y-%m-%d").date(),
            status="Pending"
        )
        tk6=Trek(
            trek_name="Ratangad Fort Trek",location="Sahyadri, Maharashtra",
            difficulty="Moderate",duration_days=2,total_slots=25,
            available_slots=21,description="Jewel fort of Maharashtra.",
            start_date=datetime.strptime("2026-08-15","%Y-%m-%d").date(),
            end_date=datetime.strptime("2026-08-16","%Y-%m-%d").date(),
            status="Open",assigned_staff_id=s_objects["Vikram Singh"].id
        )
        tk7=Trek(
            trek_name="Rajmachi Fort Trek",location="Sahyadri, Lonavala",
            difficulty="Easy",duration_days=2,total_slots=30,
            available_slots=28,description="Historic fort and fireflies trail.",
            start_date=datetime.strptime("2026-09-12","%Y-%m-%d").date(),
            end_date=datetime.strptime("2026-09-13","%Y-%m-%d").date(),
            status="Open",assigned_staff_id=s_objects["Anjali Desai"].id
        )
        tk8=Trek(
            trek_name="Harishchandragad Trek",location="Sahyadri, Bhandardara",
            difficulty="Hard",duration_days=2,total_slots=15,
            available_slots=14,description="Famous for Konkan Kada cliff.",
            start_date=datetime.strptime("2026-08-01","%Y-%m-%d").date(),
            end_date=datetime.strptime("2026-08-02","%Y-%m-%d").date(),
            status="Closed",assigned_staff_id=s_objects["Rahul Bose"].id
        )
        tk9=Trek(
            trek_name="Kalsubai Peak Trek",location="Sahyadri, Igatpuri",
            difficulty="Moderate",duration_days=2,total_slots=20,
            available_slots=17,description="Highest peak of Maharashtra.",
            start_date=datetime.strptime("2026-06-10","%Y-%m-%d").date(),
            end_date=datetime.strptime("2026-06-11","%Y-%m-%d").date(),
            status="Completed",assigned_staff_id=s_objects["Vikram Singh"].id
        )
        tk10=Trek(
            trek_name="Lohagad Fort Trek",location="Sahyadri, Pune",
            difficulty="Easy",duration_days=1,total_slots=40,
            available_slots=40,description="Iron fort with ancient Buddhist caves nearby.",
            start_date=datetime.strptime("2026-10-15","%Y-%m-%d").date(),
            end_date=datetime.strptime("2026-10-15","%Y-%m-%d").date(),
            status="Pending"
        )
        
        db.session.add_all([tk1,tk2,tk3,tk4,tk5,tk6,tk7,tk8,tk9,tk10])
        db.session.commit()

        # 18 Bookings
        bookings_data = [
            (t_objects[0].id, tk2.id, "Completed", "Paid", "Ready to explore!"),
            (t_objects[1].id, tk2.id, "Completed", "Paid", ""),
            (t_objects[2].id, tk2.id, "Completed", "Paid", "Need first aid guide"),
            (t_objects[0].id, tk3.id, "Booked", "Paid", "Vegetarian meal request"),
            (t_objects[3].id, tk3.id, "Booked", "Pending", "Will pay at base camp"),
            (t_objects[4].id, tk1.id, "Booked", "Paid", ""),
            (t_objects[5].id, tk1.id, "Booked", "Paid", "Need rental gear"),
            (t_objects[6].id, tk1.id, "Booked", "Pending", ""),
            (t_objects[7].id, tk1.id, "Cancelled", "Pending", "Medical emergency"),
            (t_objects[8].id, tk6.id, "Booked", "Paid", ""),
            (t_objects[9].id, tk6.id, "Booked", "Paid", ""),
            (t_objects[10].id, tk6.id, "Booked", "Pending", ""),
            (t_objects[11].id, tk6.id, "Booked", "Paid", ""),
            (t_objects[12].id, tk7.id, "Booked", "Paid", "Bringing kids"),
            (t_objects[13].id, tk7.id, "Booked", "Pending", ""),
            (t_objects[14].id, tk8.id, "Booked", "Paid", ""),
            (t_objects[15].id, tk9.id, "Completed", "Paid", ""),
            (t_objects[16].id, tk9.id, "Completed", "Paid", ""),
            (t_objects[17].id, tk9.id, "Completed", "Paid", "")
        ]

        for u_id, t_id, b_status, p_status, rem in bookings_data:
            bk = Booking(
                user_id=u_id, trek_id=t_id,
                booking_status=b_status, payment_status=p_status,
                remarks=rem
            )
            db.session.add(bk)
        db.session.commit()
        print("Database successfully seeded with realistic mock data!")

if __name__ == "__main__":
    run_seeder()
