from flask import Blueprint, render_template
from app.db import query

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")

@payments_bp.route("/")
def index():
    payments = query("""
        SELECT py.payment_id, b.booking_id,
               p.first_name||' '||p.last_name AS passenger,
               b.flight_id, py.amount, py.payment_mode,
               py.payment_status, py.payment_date, py.transaction_ref
        FROM payments py
        JOIN bookings b ON b.booking_id=py.booking_id
        JOIN passengers p ON p.passenger_id=b.passenger_id
        ORDER BY py.payment_id DESC
    """)
    total_rev  = query("SELECT IFNULL(SUM(amount),0) FROM payments WHERE payment_status='Success'", one=True)[0]
    total_ref  = query("SELECT IFNULL(SUM(amount),0) FROM payments WHERE payment_status='Refunded'", one=True)[0]
    return render_template("payments/index.html", payments=payments,
                           total_rev=total_rev, total_ref=total_ref)
