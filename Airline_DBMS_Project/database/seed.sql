-- ============================================================
-- SAMPLE DATA  –  Airline Reservation System
-- ============================================================

-- AIRPORTS
INSERT OR IGNORE INTO airports VALUES ('DEL','Indira Gandhi International','New Delhi','India','Asia/Kolkata');
INSERT OR IGNORE INTO airports VALUES ('BOM','Chhatrapati Shivaji Maharaj International','Mumbai','India','Asia/Kolkata');
INSERT OR IGNORE INTO airports VALUES ('BLR','Kempegowda International','Bengaluru','India','Asia/Kolkata');
INSERT OR IGNORE INTO airports VALUES ('HYD','Rajiv Gandhi International','Hyderabad','India','Asia/Kolkata');
INSERT OR IGNORE INTO airports VALUES ('MAA','Chennai International','Chennai','India','Asia/Kolkata');
INSERT OR IGNORE INTO airports VALUES ('CCU','Netaji Subhas Chandra Bose International','Kolkata','India','Asia/Kolkata');

-- ROUTES
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('DEL','BOM',1148);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('BOM','DEL',1148);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('DEL','BLR',1740);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('BLR','DEL',1740);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('DEL','HYD',1253);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('HYD','DEL',1253);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('BOM','BLR',843);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('BLR','BOM',843);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('DEL','MAA',1757);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('MAA','DEL',1757);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('DEL','CCU',1305);
INSERT OR IGNORE INTO routes(origin_airport,dest_airport,distance_km) VALUES ('CCU','DEL',1305);

-- AIRCRAFT
INSERT OR IGNORE INTO aircraft VALUES ('VT-ANK','Boeing 737-800',180,'Air India');
INSERT OR IGNORE INTO aircraft VALUES ('VT-SNY','Airbus A320',156,'IndiGo');
INSERT OR IGNORE INTO aircraft VALUES ('VT-SPK','Boeing 777-300',342,'Air India');
INSERT OR IGNORE INTO aircraft VALUES ('VT-IND','Airbus A321',194,'IndiGo');

-- SEATS for VT-ANK (180 seats – simplified 30 rows x 6 cols)
INSERT OR IGNORE INTO seats(aircraft_id,seat_number,seat_class)
WITH RECURSIVE r(row,col) AS (
    SELECT 1,'A' UNION ALL
    SELECT row+(CASE WHEN col='F' THEN 1 ELSE 0 END),
           CASE col WHEN 'A' THEN 'B' WHEN 'B' THEN 'C' WHEN 'C' THEN 'D'
                    WHEN 'D' THEN 'E' WHEN 'E' THEN 'F' ELSE 'A' END
    FROM r WHERE NOT (row=30 AND col='F')
)
SELECT 'VT-ANK', CAST(row AS TEXT)||col,
       CASE WHEN row <= 2 THEN 'Business'
            WHEN row <= 5 THEN 'First'
            ELSE 'Economy' END
FROM r;

-- SEATS for VT-SNY (156 seats – 26 rows x 6)
INSERT OR IGNORE INTO seats(aircraft_id,seat_number,seat_class)
WITH RECURSIVE r(row,col) AS (
    SELECT 1,'A' UNION ALL
    SELECT row+(CASE WHEN col='F' THEN 1 ELSE 0 END),
           CASE col WHEN 'A' THEN 'B' WHEN 'B' THEN 'C' WHEN 'C' THEN 'D'
                    WHEN 'D' THEN 'E' WHEN 'E' THEN 'F' ELSE 'A' END
    FROM r WHERE NOT (row=26 AND col='F')
)
SELECT 'VT-SNY', CAST(row AS TEXT)||col,
       CASE WHEN row <= 2 THEN 'Business' ELSE 'Economy' END
FROM r;

-- FLIGHTS
INSERT OR IGNORE INTO flights VALUES
('AI-101', 1, 'VT-ANK','2026-10-20 06:00','2026-10-20 08:00',4500,'Scheduled'),
('AI-102', 2, 'VT-ANK','2026-10-20 10:00','2026-10-20 12:00',4500,'Scheduled'),
('6E-201', 3, 'VT-SNY','2026-10-21 07:00','2026-10-21 09:30',5200,'Scheduled'),
('6E-202', 4, 'VT-SNY','2026-10-21 15:00','2026-10-21 17:30',5200,'Scheduled'),
('AI-103', 5, 'VT-ANK','2026-10-22 08:00','2026-10-22 10:10',4800,'Scheduled'),
('AI-104', 6, 'VT-ANK','2026-10-22 13:00','2026-10-22 15:10',4800,'Scheduled'),
('6E-203', 7, 'VT-SNY','2026-10-23 09:00','2026-10-23 10:45',3800,'Scheduled'),
('AI-105', 9, 'VT-ANK','2026-10-24 06:30','2026-10-24 08:45',5100,'Scheduled'),
('AI-106',11, 'VT-SPK','2026-10-25 07:00','2026-10-25 09:20',5300,'Scheduled'),
('AI-107',12, 'VT-SPK','2026-10-25 14:00','2026-10-25 16:20',5300,'Scheduled');

-- PASSENGERS
INSERT OR IGNORE INTO passengers(first_name,last_name,email,phone,passport_no,date_of_birth,nationality) VALUES
('Rahul',   'Sharma',   'rahul.sharma@email.com',   '9876543210','P1234567','1990-05-15','Indian'),
('Priya',   'Patel',    'priya.patel@email.com',    '9876543211','P2345678','1992-08-22','Indian'),
('Arjun',   'Mehta',    'arjun.mehta@email.com',    '9876543212','P3456789','1985-03-10','Indian'),
('Sneha',   'Gupta',    'sneha.gupta@email.com',    '9876543213','P4567890','1998-11-30','Indian'),
('Vikram',  'Singh',    'vikram.singh@email.com',   '9876543214','P5678901','1987-07-25','Indian'),
('Ananya',  'Reddy',    'ananya.reddy@email.com',   '9876543215','P6789012','1995-01-18','Indian'),
('Karthik', 'Nair',     'karthik.nair@email.com',   '9876543216','P7890123','1993-09-05','Indian'),
('Deepika', 'Joshi',    'deepika.joshi@email.com',  '9876543217','P8901234','1991-04-12','Indian'),
('Rohit',   'Kumar',    'rohit.kumar@email.com',    '9876543218','P9012345','1988-12-20','Indian'),
('Meera',   'Verma',    'meera.verma@email.com',    '9876543219','P0123456','1996-06-08','Indian');

-- BOOKINGS
INSERT OR IGNORE INTO bookings(passenger_id,flight_id,booking_date,booking_status,total_fare) VALUES
(1,'AI-101','2026-10-10 10:00','Confirmed',4500),
(2,'AI-101','2026-10-10 11:00','Confirmed',4500),
(3,'AI-101','2026-10-10 12:00','Confirmed',5200),
(4,'6E-201','2026-10-11 09:00','Confirmed',5200),
(5,'6E-201','2026-10-11 10:00','Confirmed',5200),
(6,'AI-103','2026-10-11 14:00','Confirmed',4800),
(7,'AI-103','2026-10-11 15:00','Cancelled',4800),
(8,'6E-203','2026-10-12 08:00','Confirmed',3800),
(9,'AI-105','2026-10-12 09:00','Confirmed',5100),
(10,'AI-106','2026-10-12 11:00','Confirmed',5300);

-- TICKETS (assign actual seats)
INSERT OR IGNORE INTO tickets(booking_id,seat_id,seat_class) VALUES
(1,(SELECT seat_id FROM seats WHERE aircraft_id='VT-ANK' AND seat_number='10A'),'Economy'),
(2,(SELECT seat_id FROM seats WHERE aircraft_id='VT-ANK' AND seat_number='10B'),'Economy'),
(3,(SELECT seat_id FROM seats WHERE aircraft_id='VT-ANK' AND seat_number='1A'),'Business'),
(4,(SELECT seat_id FROM seats WHERE aircraft_id='VT-SNY' AND seat_number='15A'),'Economy'),
(5,(SELECT seat_id FROM seats WHERE aircraft_id='VT-SNY' AND seat_number='15B'),'Economy'),
(6,(SELECT seat_id FROM seats WHERE aircraft_id='VT-ANK' AND seat_number='12A'),'Economy'),
(8,(SELECT seat_id FROM seats WHERE aircraft_id='VT-SNY' AND seat_number='8C'),'Economy'),
(9,(SELECT seat_id FROM seats WHERE aircraft_id='VT-ANK' AND seat_number='5A'),'First'),
(10,(SELECT seat_id FROM seats WHERE aircraft_id='VT-SPK' AND seat_number='20A'),'Economy');

-- CHECK-INS
INSERT OR IGNORE INTO checkins(booking_id,checkin_time,gate_number,boarding_pass) VALUES
(1,'2026-10-20 04:00','G12','BP-AI101-001'),
(2,'2026-10-20 04:30','G12','BP-AI101-002'),
(4,'2026-10-21 05:00','G7', 'BP-6E201-001'),
(5,'2026-10-21 05:15','G7', 'BP-6E201-002');

-- BAGGAGE
INSERT OR IGNORE INTO baggage(booking_id,weight_kg,baggage_type,extra_charge) VALUES
(1,22.5,'CheckedIn',0.0),
(2,18.0,'CheckedIn',0.0),
(2,6.0,'HandCarry',0.0),
(3,25.0,'CheckedIn',500.0),
(4,20.0,'CheckedIn',0.0),
(5,30.0,'CheckedIn',1000.0),
(6,15.0,'CheckedIn',0.0),
(8,12.0,'HandCarry',0.0),
(9,23.0,'CheckedIn',0.0),
(10,28.0,'CheckedIn',800.0);

-- PAYMENTS
INSERT OR IGNORE INTO payments(booking_id,amount,payment_mode,payment_status,payment_date,transaction_ref) VALUES
(1, 4500,'UPI',    'Success','2026-10-10 10:05','TXN-001'),
(2, 4500,'Card',   'Success','2026-10-10 11:05','TXN-002'),
(3, 5700,'Card',   'Success','2026-10-10 12:05','TXN-003'),
(4, 5200,'UPI',    'Success','2026-10-11 09:05','TXN-004'),
(5, 6200,'NetBanking','Success','2026-10-11 10:05','TXN-005'),
(6, 4800,'Card',   'Success','2026-10-11 14:05','TXN-006'),
(7, 4800,'UPI',    'Refunded','2026-10-11 15:05','TXN-007'),
(8, 3800,'Cash',   'Success','2026-10-12 08:05','TXN-008'),
(9, 5100,'Card',   'Success','2026-10-12 09:05','TXN-009'),
(10,6100,'UPI',    'Success','2026-10-12 11:05','TXN-010');

-- CANCELLATIONS
INSERT OR IGNORE INTO cancellations(booking_id,cancellation_date,reason,refund_amount) VALUES
(7,'2026-10-11 16:00','Change of plans',3840);
