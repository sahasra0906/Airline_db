-- ============================================================
-- AIRLINE RESERVATION & FLIGHT OPERATIONS MANAGEMENT SYSTEM
-- Database Schema – Normalized to 3NF
-- ============================================================

PRAGMA foreign_keys = ON;

-- ──────────────────────────────────────────
-- 1. AIRPORTS
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS airports (
    airport_id   TEXT PRIMARY KEY,          -- IATA code e.g. DEL
    airport_name TEXT NOT NULL,
    city         TEXT NOT NULL,
    country      TEXT NOT NULL DEFAULT 'India',
    timezone     TEXT NOT NULL DEFAULT 'Asia/Kolkata'
);

-- ──────────────────────────────────────────
-- 2. ROUTES
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS routes (
    route_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    origin_airport   TEXT NOT NULL REFERENCES airports(airport_id),
    dest_airport     TEXT NOT NULL REFERENCES airports(airport_id),
    distance_km      INTEGER CHECK (distance_km > 0),
    UNIQUE (origin_airport, dest_airport),
    CHECK (origin_airport <> dest_airport)
);

-- ──────────────────────────────────────────
-- 3. AIRCRAFT
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS aircraft (
    aircraft_id    TEXT PRIMARY KEY,        -- tail number e.g. VT-ANK
    model          TEXT NOT NULL,
    total_capacity INTEGER NOT NULL CHECK (total_capacity > 0),
    airline_name   TEXT NOT NULL DEFAULT 'AirIndia'
);

-- ──────────────────────────────────────────
-- 4. SEATS
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS seats (
    seat_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    aircraft_id TEXT NOT NULL REFERENCES aircraft(aircraft_id) ON DELETE CASCADE,
    seat_number TEXT NOT NULL,              -- e.g. 12A
    seat_class  TEXT NOT NULL DEFAULT 'Economy'
                CHECK (seat_class IN ('Economy','Business','First')),
    UNIQUE (aircraft_id, seat_number)
);

-- ──────────────────────────────────────────
-- 5. FLIGHTS (SCHEDULES)
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS flights (
    flight_id        TEXT PRIMARY KEY,      -- e.g. AI-101
    route_id         INTEGER NOT NULL REFERENCES routes(route_id),
    aircraft_id      TEXT NOT NULL REFERENCES aircraft(aircraft_id),
    departure_time   TEXT NOT NULL,         -- ISO-8601 datetime
    arrival_time     TEXT NOT NULL,
    base_fare        REAL NOT NULL CHECK (base_fare >= 0),
    status           TEXT NOT NULL DEFAULT 'Scheduled'
                     CHECK (status IN ('Scheduled','Delayed','Cancelled','Completed')),
    CHECK (arrival_time > departure_time)
);

-- ──────────────────────────────────────────
-- 6. PASSENGERS
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS passengers (
    passenger_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    phone         TEXT,
    passport_no   TEXT UNIQUE,
    date_of_birth TEXT,
    nationality   TEXT DEFAULT 'Indian',
    created_at    TEXT DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────
-- 7. BOOKINGS
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    booking_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    passenger_id   INTEGER NOT NULL REFERENCES passengers(passenger_id),
    flight_id      TEXT NOT NULL REFERENCES flights(flight_id),
    booking_date   TEXT NOT NULL DEFAULT (datetime('now')),
    booking_status TEXT NOT NULL DEFAULT 'Confirmed'
                   CHECK (booking_status IN ('Confirmed','Cancelled','Pending')),
    total_fare     REAL NOT NULL CHECK (total_fare >= 0)
);

-- ──────────────────────────────────────────
-- 8. TICKETS  (one seat per passenger per flight enforced here)
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id   INTEGER NOT NULL REFERENCES bookings(booking_id),
    seat_id      INTEGER NOT NULL REFERENCES seats(seat_id),
    seat_class   TEXT NOT NULL DEFAULT 'Economy'
                 CHECK (seat_class IN ('Economy','Business','First')),
    issue_date   TEXT NOT NULL DEFAULT (datetime('now')),
    ticket_status TEXT NOT NULL DEFAULT 'Active'
                  CHECK (ticket_status IN ('Active','Cancelled','Used')),
    UNIQUE (booking_id, seat_id)             -- one seat per booking line
);

-- One seat per passenger per flight:
CREATE UNIQUE INDEX IF NOT EXISTS uidx_passenger_flight
    ON bookings(passenger_id, flight_id)
    WHERE booking_status <> 'Cancelled';

-- ──────────────────────────────────────────
-- 9. CHECK-INS  (only for confirmed bookings)
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS checkins (
    checkin_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id      INTEGER NOT NULL UNIQUE REFERENCES bookings(booking_id),
    checkin_time    TEXT NOT NULL DEFAULT (datetime('now')),
    gate_number     TEXT,
    boarding_pass   TEXT UNIQUE              -- generated boarding-pass number
);

-- ──────────────────────────────────────────
-- 10. BAGGAGE
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS baggage (
    baggage_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id     INTEGER NOT NULL REFERENCES bookings(booking_id),
    weight_kg      REAL NOT NULL CHECK (weight_kg >= 0),  -- non-negative
    baggage_type   TEXT NOT NULL DEFAULT 'CheckedIn'
                   CHECK (baggage_type IN ('CheckedIn','HandCarry')),
    extra_charge   REAL NOT NULL DEFAULT 0.0 CHECK (extra_charge >= 0)
);

-- ──────────────────────────────────────────
-- 11. PAYMENTS
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS payments (
    payment_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id     INTEGER NOT NULL REFERENCES bookings(booking_id),
    amount         REAL NOT NULL CHECK (amount > 0),
    payment_mode   TEXT NOT NULL DEFAULT 'Card'
                   CHECK (payment_mode IN ('Card','UPI','NetBanking','Cash')),
    payment_status TEXT NOT NULL DEFAULT 'Success'
                   CHECK (payment_status IN ('Success','Failed','Refunded','Pending')),
    payment_date   TEXT NOT NULL DEFAULT (datetime('now')),
    transaction_ref TEXT UNIQUE
);

-- ──────────────────────────────────────────
-- 12. CANCELLATIONS
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cancellations (
    cancellation_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id        INTEGER NOT NULL UNIQUE REFERENCES bookings(booking_id),
    cancellation_date TEXT NOT NULL DEFAULT (datetime('now')),
    reason            TEXT,
    refund_amount     REAL NOT NULL DEFAULT 0.0 CHECK (refund_amount >= 0)
);

-- ──────────────────────────────────────────
-- INDEXES for frequently searched attributes
-- ──────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_flights_departure  ON flights(departure_time);
CREATE INDEX IF NOT EXISTS idx_flights_route      ON flights(route_id);
CREATE INDEX IF NOT EXISTS idx_bookings_passenger ON bookings(passenger_id);
CREATE INDEX IF NOT EXISTS idx_bookings_flight    ON bookings(flight_id);
CREATE INDEX IF NOT EXISTS idx_tickets_booking    ON tickets(booking_id);
CREATE INDEX IF NOT EXISTS idx_payments_booking   ON payments(booking_id);

-- ──────────────────────────────────────────
-- VIEWS
-- ──────────────────────────────────────────

-- Flight Manifest View
CREATE VIEW IF NOT EXISTS vw_flight_manifest AS
SELECT
    f.flight_id,
    f.departure_time,
    f.arrival_time,
    f.status AS flight_status,
    r.origin_airport  || ' → ' || r.dest_airport AS route,
    p.passenger_id,
    p.first_name || ' ' || p.last_name AS passenger_name,
    p.passport_no,
    s.seat_number,
    t.seat_class,
    b.booking_status,
    t.ticket_status
FROM flights f
JOIN routes r   ON f.route_id   = r.route_id
JOIN bookings b ON b.flight_id  = f.flight_id
JOIN tickets t  ON t.booking_id = b.booking_id
JOIN seats s    ON s.seat_id    = t.seat_id
JOIN passengers p ON p.passenger_id = b.passenger_id;

-- Occupancy View
CREATE VIEW IF NOT EXISTS vw_occupancy AS
SELECT
    f.flight_id,
    f.departure_time,
    a.total_capacity,
    COUNT(CASE WHEN b.booking_status = 'Confirmed' THEN 1 END) AS booked_seats,
    ROUND(COUNT(CASE WHEN b.booking_status = 'Confirmed' THEN 1 END) * 100.0 / a.total_capacity, 2) AS occupancy_pct
FROM flights f
JOIN aircraft a  ON a.aircraft_id = f.aircraft_id
LEFT JOIN bookings b ON b.flight_id = f.flight_id
GROUP BY f.flight_id;

-- Revenue View
CREATE VIEW IF NOT EXISTS vw_revenue AS
SELECT
    f.flight_id,
    r.origin_airport || ' → ' || r.dest_airport AS route,
    COUNT(py.payment_id) AS total_payments,
    ROUND(SUM(CASE WHEN py.payment_status='Success' THEN py.amount ELSE 0 END),2) AS total_revenue,
    ROUND(SUM(CASE WHEN py.payment_status='Refunded' THEN py.amount ELSE 0 END),2) AS total_refunds
FROM flights f
JOIN routes r    ON f.route_id = r.route_id
JOIN bookings b  ON b.flight_id = f.flight_id
JOIN payments py ON py.booking_id = b.booking_id
GROUP BY f.flight_id;
