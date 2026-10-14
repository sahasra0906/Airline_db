from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.db import query, mutate

flights_bp = Blueprint("flights", __name__, url_prefix="/flights")

@flights_bp.route("/")
def index():
    orig = request.args.get("origin", "")
    dest = request.args.get("dest", "")
    date = request.args.get("date", "")
    cls  = request.args.get("cls", "")

    sql = """
        SELECT f.flight_id, r.origin_airport, r.dest_airport,
               r.origin_airport||' → '||r.dest_airport AS route,
               f.departure_time, f.arrival_time, f.base_fare, f.status,
               a.model, a.total_capacity,
               (SELECT COUNT(*) FROM bookings b WHERE b.flight_id=f.flight_id
                AND b.booking_status='Confirmed') AS booked
        FROM flights f
        JOIN routes r  ON f.route_id  = r.route_id
        JOIN aircraft a ON a.aircraft_id = f.aircraft_id
        WHERE (? = '' OR r.origin_airport = ?)
          AND (? = '' OR r.dest_airport   = ?)
          AND (? = '' OR date(f.departure_time) = date(?))
        ORDER BY f.departure_time
    """
    flights = query(sql, (orig,orig, dest,dest, date,date))
    airports = query("SELECT airport_id, city FROM airports ORDER BY city")
    return render_template("flights/index.html", flights=flights,
                           airports=airports, orig=orig, dest=dest,
                           date=date, cls=cls)

@flights_bp.route("/<flight_id>")
def detail(flight_id):
    flight = query("""
        SELECT f.*, r.origin_airport, r.dest_airport,
               r.origin_airport||' → '||r.dest_airport AS route,
               a.model, a.total_capacity,
               (SELECT COUNT(*) FROM bookings b WHERE b.flight_id=f.flight_id
                AND b.booking_status='Confirmed') AS booked
        FROM flights f
        JOIN routes r ON f.route_id=r.route_id
        JOIN aircraft a ON a.aircraft_id=f.aircraft_id
        WHERE f.flight_id=?
    """, (flight_id,), one=True)
    manifest = query("""
        SELECT p.first_name||' '||p.last_name AS name, s.seat_number,
               t.seat_class, b.booking_status, t.ticket_status
        FROM bookings b
        JOIN passengers p ON p.passenger_id=b.passenger_id
        JOIN tickets t ON t.booking_id=b.booking_id
        JOIN seats s ON s.seat_id=t.seat_id
        WHERE b.flight_id=? ORDER BY s.seat_number
    """, (flight_id,))
    return render_template("flights/detail.html", flight=flight, manifest=manifest)
