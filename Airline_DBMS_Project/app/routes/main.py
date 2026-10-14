import random, string
from flask import Blueprint, render_template
from app.db import query

main_bp = Blueprint("main", __name__)

def gen_stats():
    return {
        "flights":     query("SELECT COUNT(*) FROM flights", one=True)[0],
        "passengers":  query("SELECT COUNT(*) FROM passengers", one=True)[0],
        "bookings":    query("SELECT COUNT(*) FROM bookings WHERE booking_status='Confirmed'", one=True)[0],
        "revenue":     query("SELECT IFNULL(SUM(amount),0) FROM payments WHERE payment_status='Success'", one=True)[0],
        "cancelled":   query("SELECT COUNT(*) FROM bookings WHERE booking_status='Cancelled'", one=True)[0],
        "checkins":    query("SELECT COUNT(*) FROM checkins", one=True)[0],
    }

@main_bp.route("/")
def dashboard():
    stats = gen_stats()
    recent_bookings = query("""
        SELECT b.booking_id, p.first_name||' '||p.last_name AS passenger,
               b.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               b.booking_date, b.booking_status, b.total_fare
        FROM bookings b
        JOIN passengers p ON p.passenger_id=b.passenger_id
        JOIN flights f ON f.flight_id=b.flight_id
        JOIN routes r ON r.route_id=f.route_id
        ORDER BY b.booking_id DESC LIMIT 6
    """)
    upcoming = query("""
        SELECT f.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               f.departure_time, f.arrival_time, f.status, f.base_fare,
               a.total_capacity,
               (SELECT COUNT(*) FROM bookings b2 WHERE b2.flight_id=f.flight_id
                AND b2.booking_status='Confirmed') AS booked
        FROM flights f
        JOIN routes r ON f.route_id=r.route_id
        JOIN aircraft a ON a.aircraft_id=f.aircraft_id
        WHERE f.status='Scheduled'
        ORDER BY f.departure_time LIMIT 5
    """)
    return render_template("index.html", stats=stats,
                           recent_bookings=recent_bookings, upcoming=upcoming)
