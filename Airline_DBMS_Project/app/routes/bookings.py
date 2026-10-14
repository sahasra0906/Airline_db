import random, string
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.db import query, mutate, mutate_many, get_db
import sqlite3

bookings_bp = Blueprint("bookings", __name__, url_prefix="/bookings")

def gen_ref(prefix="TXN"):
    return prefix + "-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

@bookings_bp.route("/")
def index():
    bookings = query("""
        SELECT b.booking_id, p.first_name||' '||p.last_name AS passenger,
               b.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               f.departure_time, b.booking_date, b.booking_status, b.total_fare
        FROM bookings b
        JOIN passengers p ON p.passenger_id=b.passenger_id
        JOIN flights f ON f.flight_id=b.flight_id
        JOIN routes r ON r.route_id=f.route_id
        ORDER BY b.booking_id DESC
    """)
    return render_template("bookings/index.html", bookings=bookings)

@bookings_bp.route("/new", methods=["GET","POST"])
def new():
    passengers = query("SELECT passenger_id, first_name||' '||last_name AS name, email FROM passengers ORDER BY first_name")
    flights    = query("""
        SELECT f.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               f.departure_time, f.base_fare, f.status, a.total_capacity,
               (SELECT COUNT(*) FROM bookings b WHERE b.flight_id=f.flight_id
                AND b.booking_status='Confirmed') AS booked
        FROM flights f
        JOIN routes r ON f.route_id=r.route_id
        JOIN aircraft a ON a.aircraft_id=f.aircraft_id
        WHERE f.status='Scheduled'
        ORDER BY f.departure_time
    """)

    if request.method == "POST":
        pid    = request.form.get("passenger_id")
        fid    = request.form.get("flight_id")
        cls    = request.form.get("seat_class","Economy")
        paymod = request.form.get("payment_mode","Card")

        if not pid or not fid:
            flash("Select both passenger and flight.", "danger")
            return render_template("bookings/new.html", passengers=passengers, flights=flights)

        # Duplicate check
        dup = query("""
            SELECT booking_id FROM bookings
            WHERE passenger_id=? AND flight_id=? AND booking_status<>'Cancelled'
        """, (pid, fid), one=True)
        if dup:
            flash("This passenger already has an active booking for this flight.", "danger")
            return render_template("bookings/new.html", passengers=passengers, flights=flights)

        fare_row = query("SELECT base_fare FROM flights WHERE flight_id=?", (fid,), one=True)
        base_fare = fare_row[0] if fare_row else 0
        extra     = 1500 if cls=="Business" else 3000 if cls=="First" else 0
        total     = base_fare + extra

        # Find available seat
        seat = query("""
            SELECT seat_id, seat_number FROM seats
            WHERE aircraft_id=(SELECT aircraft_id FROM flights WHERE flight_id=?)
              AND seat_class=?
              AND seat_id NOT IN (
                  SELECT t.seat_id FROM tickets t
                  JOIN bookings b ON b.booking_id=t.booking_id
                  WHERE b.flight_id=? AND b.booking_status='Confirmed'
              )
            LIMIT 1
        """, (fid, cls, fid), one=True)
        if not seat:
            flash(f"No {cls} seats available for this flight.", "danger")
            return render_template("bookings/new.html", passengers=passengers, flights=flights)

        ref = gen_ref()
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO bookings(passenger_id,flight_id,booking_status,total_fare)
                VALUES(?,?,'Confirmed',?)
            """, (pid, fid, total))
            bid = cur.lastrowid
            cur.execute("INSERT INTO tickets(booking_id,seat_id,seat_class) VALUES(?,?,?)",
                        (bid, seat["seat_id"], cls))
            cur.execute("""
                INSERT INTO payments(booking_id,amount,payment_mode,payment_status,transaction_ref)
                VALUES(?,?,?,'Success',?)
            """, (bid, total, paymod, ref))
            conn.commit()
            flash(f"Booking #{bid} confirmed! Seat {seat['seat_number']} | ₹{total:,.0f} | Ref: {ref}", "success")
            return redirect(url_for("bookings.index"))
        except sqlite3.Error as e:
            conn.rollback()
            flash(str(e), "danger")
        finally:
            conn.close()

    return render_template("bookings/new.html", passengers=passengers, flights=flights)

@bookings_bp.route("/<int:bid>")
def detail(bid):
    booking = query("""
        SELECT b.*, p.first_name||' '||p.last_name AS passenger,
               p.email, p.phone, p.passport_no,
               f.departure_time, f.arrival_time, f.status AS flight_status,
               r.origin_airport||' → '||r.dest_airport AS route
        FROM bookings b
        JOIN passengers p ON p.passenger_id=b.passenger_id
        JOIN flights f ON f.flight_id=b.flight_id
        JOIN routes r ON r.route_id=f.route_id
        WHERE b.booking_id=?
    """, (bid,), one=True)
    ticket  = query("""
        SELECT t.*, s.seat_number FROM tickets t
        JOIN seats s ON s.seat_id=t.seat_id
        WHERE t.booking_id=?
    """, (bid,), one=True)
    payment = query("SELECT * FROM payments WHERE booking_id=?", (bid,), one=True)
    checkin = query("SELECT * FROM checkins WHERE booking_id=?", (bid,), one=True)
    baggage = query("SELECT * FROM baggage WHERE booking_id=?", (bid,))
    return render_template("bookings/detail.html", booking=booking,
                           ticket=ticket, payment=payment,
                           checkin=checkin, baggage=baggage)
