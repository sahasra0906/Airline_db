from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.db import query, mutate
import sqlite3

passengers_bp = Blueprint("passengers", __name__, url_prefix="/passengers")

@passengers_bp.route("/")
def index():
    passengers = query("""
        SELECT p.*,
               (SELECT COUNT(*) FROM bookings b WHERE b.passenger_id=p.passenger_id) AS booking_count
        FROM passengers p ORDER BY p.first_name
    """)
    return render_template("passengers/index.html", passengers=passengers)

@passengers_bp.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        fn  = request.form.get("first_name","").strip()
        ln  = request.form.get("last_name","").strip()
        em  = request.form.get("email","").strip()
        ph  = request.form.get("phone","").strip() or None
        pp  = request.form.get("passport_no","").strip() or None
        dob = request.form.get("date_of_birth","").strip() or None
        nat = request.form.get("nationality","Indian").strip()

        if not fn or not ln or not em:
            flash("First name, Last name and Email are required.", "danger")
            return redirect(url_for("passengers.add"))
        try:
            mutate("""
                INSERT INTO passengers(first_name,last_name,email,phone,passport_no,date_of_birth,nationality)
                VALUES(?,?,?,?,?,?,?)
            """, (fn, ln, em, ph, pp, dob, nat))
            flash(f"Passenger {fn} {ln} added successfully.", "success")
            return redirect(url_for("passengers.index"))
        except sqlite3.IntegrityError:
            flash("Email or Passport number already exists.", "danger")
    return render_template("passengers/add.html")

@passengers_bp.route("/<int:pid>")
def detail(pid):
    p = query("SELECT * FROM passengers WHERE passenger_id=?", (pid,), one=True)
    bookings = query("""
        SELECT b.*, f.flight_id,
               r.origin_airport||' → '||r.dest_airport AS route,
               f.departure_time
        FROM bookings b
        JOIN flights f ON f.flight_id=b.flight_id
        JOIN routes r ON r.route_id=f.route_id
        WHERE b.passenger_id=? ORDER BY b.booking_id DESC
    """, (pid,))
    return render_template("passengers/detail.html", p=p, bookings=bookings)
