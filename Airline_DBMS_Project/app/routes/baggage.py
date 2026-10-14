from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.db import query, mutate

baggage_bp = Blueprint("baggage", __name__, url_prefix="/baggage")

@baggage_bp.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        bid  = request.form.get("booking_id","").strip()
        wt   = request.form.get("weight","").strip()
        btyp = request.form.get("baggage_type","CheckedIn")
        try:
            wt_f = float(wt)
            if wt_f < 0:
                raise ValueError("Weight must be non-negative")
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("baggage.index"))

        bk = query("SELECT * FROM bookings WHERE booking_id=? AND booking_status='Confirmed'",
                   (bid,), one=True)
        if not bk:
            flash("No confirmed booking with that ID.", "danger")
        else:
            extra = max(0, (wt_f - 25)) * 500 if btyp == "CheckedIn" else 0
            mutate("INSERT INTO baggage(booking_id,weight_kg,baggage_type,extra_charge) VALUES(?,?,?,?)",
                   (bid, wt_f, btyp, extra))
            flash(f"Baggage added. Extra charge: ₹{extra:,.0f}", "success")

    records = query("""
        SELECT bg.baggage_id, b.booking_id,
               p.first_name||' '||p.last_name AS passenger,
               b.flight_id, bg.weight_kg, bg.baggage_type, bg.extra_charge
        FROM baggage bg
        JOIN bookings b ON b.booking_id=bg.booking_id
        JOIN passengers p ON p.passenger_id=b.passenger_id
        ORDER BY bg.baggage_id DESC
    """)
    return render_template("baggage/index.html", records=records)
