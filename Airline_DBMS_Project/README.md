# Airline Reservation & Flight Operations Management System

> **PROJECT 18** – Design and Implementation of a Database Management System for Airline Reservation and Flight Operations Management System

## Project Structure

```
airline project/
├── app/                     # Flask application package
│   ├── __init__.py          # App factory
│   ├── db.py                # Database helper (SQLite)
│   └── routes/              # One blueprint per feature
│       ├── main.py          # Dashboard
│       ├── flights.py       # Flight search & detail
│       ├── passengers.py    # Passenger management
│       ├── bookings.py      # Booking + seat allocation + payment
│       ├── tickets.py       # Ticket issuance
│       ├── checkin.py       # Check-in & boarding pass
│       ├── baggage.py       # Baggage entry
│       ├── cancellations.py # Cancellation + refund
│       ├── payments.py      # Payment records
│       └── reports.py       # All reports
├── static/css/style.css     # Complete CSS
├── templates/               # Jinja2 HTML templates
├── database/
│   ├── schema.sql           # DDL – 12 tables, views, indexes (3NF)
│   ├── seed.sql             # Sample data
│   └── airline.db           # SQLite database (auto-created)
├── app.py                   # Entry point
├── run.bat                  # Windows double-click launcher
└── requirements.txt
```

## Setup & Run

```bash
pip install flask
python app.py
```

Or double-click **run.bat** – it opens the browser automatically.

Visit **http://127.0.0.1:5000**

## Features

| Module | Description |
|--------|-------------|
| Dashboard | Stats, upcoming flights, recent bookings |
| Flight Search | Filter by origin, destination, date |
| Passengers | Add & view passenger records |
| Bookings | Create booking with auto seat allocation & payment |
| Tickets | View issued tickets |
| Check-In | Check in confirmed passengers, generate boarding pass |
| Baggage | Add baggage with weight validation & excess charges |
| Cancellations | Cancel booking with 80% refund rule |
| Payments | View all transactions |
| Reports | Manifest, Occupancy, Revenue, Baggage, Cancellations, On-Time |

## Database Schema (3NF)

**Tables:** airports, routes, aircraft, seats, flights, passengers, bookings, tickets, checkins, baggage, payments, cancellations

**Views:** vw_flight_manifest, vw_occupancy, vw_revenue

**Indexes:** On departure_time, route_id, passenger_id, flight_id, booking_id

## Business Rules Enforced

- One seat per passenger per flight (UNIQUE index)
- Aircraft capacity limits (available seats shown live)
- Non-negative baggage weight (CHECK constraint + UI validation)
- Check-in only for Confirmed bookings
- 80% refund on cancellation
- Foreign keys enforced throughout
