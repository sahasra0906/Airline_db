from flask import Blueprint, render_template
from app.db import query

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route("/")
def index():
    return render_template("reports/index.html")

@reports_bp.route("/manifest")
def manifest():
    rows = query("""
        SELECT f.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               f.departure_time, p.first_name||' '||p.last_name AS passenger,
               p.passport_no, s.seat_number, t.seat_class,
               b.booking_status, t.ticket_status
        FROM flights f
        JOIN routes r ON f.route_id=r.route_id
        JOIN bookings b ON b.flight_id=f.flight_id
        JOIN passengers p ON p.passenger_id=b.passenger_id
        JOIN tickets t ON t.booking_id=b.booking_id
        JOIN seats s ON s.seat_id=t.seat_id
        ORDER BY f.flight_id, s.seat_number
    """)
    return render_template("reports/manifest.html", rows=rows)

@reports_bp.route("/occupancy")
def occupancy():
    rows = query("""
        SELECT f.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               f.departure_time, a.total_capacity,
               COUNT(CASE WHEN b.booking_status='Confirmed' THEN 1 END) AS booked,
               ROUND(COUNT(CASE WHEN b.booking_status='Confirmed' THEN 1 END)*100.0/a.total_capacity,1) AS pct
        FROM flights f
        JOIN routes r ON f.route_id=r.route_id
        JOIN aircraft a ON a.aircraft_id=f.aircraft_id
        LEFT JOIN bookings b ON b.flight_id=f.flight_id
        GROUP BY f.flight_id
        ORDER BY pct DESC
    """)
    return render_template("reports/occupancy.html", rows=rows)

@reports_bp.route("/revenue")
def revenue():
    rows = query("""
        SELECT f.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               COUNT(py.payment_id) AS payments,
               ROUND(SUM(CASE WHEN py.payment_status='Success'  THEN py.amount ELSE 0 END),2) AS revenue,
               ROUND(SUM(CASE WHEN py.payment_status='Refunded' THEN py.amount ELSE 0 END),2) AS refunds
        FROM flights f
        JOIN routes r ON f.route_id=r.route_id
        JOIN bookings b ON b.flight_id=f.flight_id
        JOIN payments py ON py.booking_id=b.booking_id
        GROUP BY f.flight_id
        ORDER BY revenue DESC
    """)
    return render_template("reports/revenue.html", rows=rows)

@reports_bp.route("/baggage")
def baggage():
    rows = query("""
        SELECT b.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               p.first_name||' '||p.last_name AS passenger,
               bg.weight_kg, bg.baggage_type, bg.extra_charge
        FROM baggage bg
        JOIN bookings b ON b.booking_id=bg.booking_id
        JOIN passengers p ON p.passenger_id=b.passenger_id
        JOIN flights f ON f.flight_id=b.flight_id
        JOIN routes r ON r.route_id=f.route_id
        ORDER BY b.flight_id
    """)
    return render_template("reports/baggage.html", rows=rows)

@reports_bp.route("/cancellations")
def cancellations():
    rows = query("""
        SELECT c.cancellation_id, b.booking_id,
               p.first_name||' '||p.last_name AS passenger,
               b.flight_id, c.cancellation_date, c.reason, c.refund_amount
        FROM cancellations c
        JOIN bookings b ON b.booking_id=c.booking_id
        JOIN passengers p ON p.passenger_id=b.passenger_id
        ORDER BY c.cancellation_date DESC
    """)
    return render_template("reports/cancellations.html", rows=rows)

@reports_bp.route("/ontime")
def ontime():
    rows = query("""
        SELECT f.flight_id, r.origin_airport||' → '||r.dest_airport AS route,
               f.departure_time, f.arrival_time, f.status, a.model AS aircraft
        FROM flights f
        JOIN routes r ON f.route_id=r.route_id
        JOIN aircraft a ON a.aircraft_id=f.aircraft_id
        ORDER BY f.departure_time
    """)
    on_time  = sum(1 for r in rows if r["status"]=="Scheduled" or r["status"]=="Completed")
    return render_template("reports/ontime.html", rows=rows, on_time=on_time)
