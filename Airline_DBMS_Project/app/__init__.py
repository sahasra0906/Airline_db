from flask import Flask
from .db import init_db


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = "airline-dbms-secret-2026"

    from .routes.main          import main_bp
    from .routes.flights       import flights_bp
    from .routes.passengers    import passengers_bp
    from .routes.bookings      import bookings_bp
    from .routes.tickets       import tickets_bp
    from .routes.checkin       import checkin_bp
    from .routes.baggage       import baggage_bp
    from .routes.cancellations import cancellations_bp
    from .routes.payments      import payments_bp
    from .routes.reports       import reports_bp

    for bp in [main_bp, flights_bp, passengers_bp, bookings_bp,
               tickets_bp, checkin_bp, baggage_bp, cancellations_bp,
               payments_bp, reports_bp]:
        app.register_blueprint(bp)

    with app.app_context():
        init_db()

    return app
