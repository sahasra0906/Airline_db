import random, string
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.db import query, mutate

checkin_bp = Blueprint("checkin", __name__, url_prefix="/checkin")

def gen_bp():
    return "BP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

@checkin_bp.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        bid  = request.form.get("booking_id","").strip()
        gate = request.form.get("gate","TBD").strip()
        if not bid:
            flash("Enter a Booking ID.", "danger")
        else:
            bk = query("SELECT * FROM bookings WHERE booking_id=?", (bid,), one=True)
            if not bk:
                flash("Booking not found.", "danger")
            elif bk["booking_status"] != "Confirmed":
                flash("Only Confirmed bookings can check in.", "warning")
            elif query("SELECT checkin_id FROM checkins WHERE booking_id=?", (bid,), one=True):
                flash("Passenger already checked in.", "warning")
            else:
                bp = gen_bp()
                mutate("INSERT INTO checkins(booking_id,gate_number,boarding_pass) VALUES(?,?,?)",
                       (bid, gate or "TBD", bp))
                flash(f"Check-in successful! Boarding Pass: {bp}", "success")

    checkins = query("""
        SELECT ci.checkin_id, b.booking_id,
               p.first_name||' '||p.last_name AS passenger,
               b.flight_id, s.seat_number, ci.gate_number,
               ci.checkin_time, ci.boarding_pass
        FROM checkins ci
        JOIN bookings b ON b.booking_id=ci.booking_id
        JOIN passengers p ON p.passenger_id=b.passenger_id
        JOIN tickets t ON t.booking_id=b.booking_id
        JOIN seats s ON s.seat_id=t.seat_id
        ORDER BY ci.checkin_id DESC
    """)
    return render_template("checkin/index.html", checkins=checkins)
