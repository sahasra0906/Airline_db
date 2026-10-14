from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.db import query, get_db
import sqlite3

cancellations_bp = Blueprint("cancellations", __name__, url_prefix="/cancellations")

@cancellations_bp.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        bid    = request.form.get("booking_id","").strip()
        reason = request.form.get("reason","Customer request").strip()
        bk = query("SELECT * FROM bookings WHERE booking_id=?", (bid,), one=True)
        if not bk:
            flash("Booking not found.", "danger")
        elif bk["booking_status"] == "Cancelled":
            flash("Booking already cancelled.", "warning")
        else:
            refund = round(bk["total_fare"] * 0.80, 2)
            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute("UPDATE bookings SET booking_status='Cancelled' WHERE booking_id=?", (bid,))
                cur.execute("UPDATE tickets SET ticket_status='Cancelled' WHERE booking_id=?", (bid,))
                cur.execute("""
                    INSERT OR IGNORE INTO cancellations(booking_id,reason,refund_amount)
                    VALUES(?,?,?)
                """, (bid, reason, refund))
                cur.execute("UPDATE payments SET payment_status='Refunded' WHERE booking_id=?", (bid,))
                conn.commit()
                flash(f"Booking #{bid} cancelled. Refund ₹{refund:,.0f} initiated.", "success")
            except sqlite3.Error as e:
                conn.rollback()
                flash(str(e), "danger")
            finally:
                conn.close()

    records = query("""
        SELECT c.cancellation_id, b.booking_id,
               p.first_name||' '||p.last_name AS passenger,
               b.flight_id, c.cancellation_date,
               c.reason, c.refund_amount, b.total_fare
        FROM cancellations c
        JOIN bookings b ON b.booking_id=c.booking_id
        JOIN passengers p ON p.passenger_id=b.passenger_id
        ORDER BY c.cancellation_id DESC
    """)
    return render_template("cancellations/index.html", records=records)
