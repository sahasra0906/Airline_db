from flask import Blueprint, render_template
from app.db import query

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")

@tickets_bp.route("/")
def index():
    tickets = query("""
        SELECT t.ticket_id, b.booking_id,
               p.first_name||' '||p.last_name AS passenger,
               b.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               f.departure_time, s.seat_number, t.seat_class,
               t.issue_date, t.ticket_status, b.total_fare
        FROM tickets t
        JOIN bookings b ON b.booking_id=t.booking_id
        JOIN passengers p ON p.passenger_id=b.passenger_id
        JOIN flights f ON f.flight_id=b.flight_id
        JOIN routes r ON r.route_id=f.route_id
        JOIN seats s ON s.seat_id=t.seat_id
        ORDER BY t.ticket_id DESC
    """)
    return render_template("tickets/index.html", tickets=tickets)
