-- ============================================================
--  LifeLineDB — Hospital Management Database Schema
--  Normalized to 3NF | MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS LifeLineDB;
USE LifeLineDB;

-- ─────────────────────────────────────────
--  1. DEPARTMENTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Departments (
    dept_id       INT AUTO_INCREMENT PRIMARY KEY,
    dept_name     VARCHAR(100) NOT NULL UNIQUE,
    location      VARCHAR(100),
    head_doctor   VARCHAR(100),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
--  2. DOCTORS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Doctors (
    doctor_id     INT AUTO_INCREMENT PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    specialization VARCHAR(100),
    phone         VARCHAR(15)  UNIQUE,
    email         VARCHAR(100) UNIQUE,
    dept_id       INT,
    joining_date  DATE,
    CONSTRAINT fk_doctor_dept FOREIGN KEY (dept_id)
        REFERENCES Departments(dept_id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────
--  3. PATIENTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Patients (
    patient_id    INT AUTO_INCREMENT PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    dob           DATE,
    gender        ENUM('Male','Female','Other'),
    blood_group   VARCHAR(5),
    phone         VARCHAR(15)  UNIQUE,
    email         VARCHAR(100),
    address       TEXT,
    emergency_contact VARCHAR(15),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
--  4. ROOMS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Rooms (
    room_id       INT AUTO_INCREMENT PRIMARY KEY,
    room_number   VARCHAR(10)  NOT NULL UNIQUE,
    room_type     ENUM('General','ICU','Private','Semi-Private') NOT NULL,
    floor         INT,
    capacity      INT DEFAULT 1,
    status        ENUM('Available','Occupied','Maintenance') DEFAULT 'Available',
    daily_rate    DECIMAL(10,2) NOT NULL
);

-- ─────────────────────────────────────────
--  5. APPOINTMENTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id  INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    reason          TEXT,
    status          ENUM('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_appt_patient FOREIGN KEY (patient_id)
        REFERENCES Patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_appt_doctor  FOREIGN KEY (doctor_id)
        REFERENCES Doctors(doctor_id)  ON DELETE CASCADE
);

-- ─────────────────────────────────────────
--  6. ADMISSIONS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Admissions (
    admission_id    INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    room_id         INT NOT NULL,
    admission_date  DATE NOT NULL,
    discharge_date  DATE,
    diagnosis       TEXT,
    status          ENUM('Admitted','Discharged') DEFAULT 'Admitted',
    CONSTRAINT fk_adm_patient FOREIGN KEY (patient_id)
        REFERENCES Patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_adm_doctor  FOREIGN KEY (doctor_id)
        REFERENCES Doctors(doctor_id)  ON DELETE CASCADE,
    CONSTRAINT fk_adm_room    FOREIGN KEY (room_id)
        REFERENCES Rooms(room_id)      ON DELETE RESTRICT
);

-- ─────────────────────────────────────────
--  7. PRESCRIPTIONS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    appointment_id  INT,
    prescribed_date DATE NOT NULL,
    medicine_name   VARCHAR(200) NOT NULL,
    dosage          VARCHAR(100),
    duration        VARCHAR(50),
    instructions    TEXT,
    CONSTRAINT fk_rx_patient FOREIGN KEY (patient_id)
        REFERENCES Patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_rx_doctor  FOREIGN KEY (doctor_id)
        REFERENCES Doctors(doctor_id)  ON DELETE CASCADE,
    CONSTRAINT fk_rx_appt    FOREIGN KEY (appointment_id)
        REFERENCES Appointments(appointment_id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────
--  8. BILLING
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Billing (
    bill_id         INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    admission_id    INT,
    bill_date       DATE NOT NULL,
    consultation_fee DECIMAL(10,2) DEFAULT 0,
    room_charges    DECIMAL(10,2) DEFAULT 0,
    medicine_charges DECIMAL(10,2) DEFAULT 0,
    other_charges   DECIMAL(10,2) DEFAULT 0,
    total_amount    DECIMAL(10,2) GENERATED ALWAYS AS
                    (consultation_fee + room_charges + medicine_charges + other_charges) STORED,
    payment_status  ENUM('Pending','Paid','Partial') DEFAULT 'Pending',
    payment_method  ENUM('Cash','Card','Insurance','Online') DEFAULT 'Cash',
    CONSTRAINT fk_bill_patient FOREIGN KEY (patient_id)
        REFERENCES Patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_bill_adm    FOREIGN KEY (admission_id)
        REFERENCES Admissions(admission_id) ON DELETE SET NULL
);

-- ============================================================
--  TRIGGERS
-- ============================================================

DELIMITER $$

-- Auto-mark room as Occupied when patient is admitted
CREATE TRIGGER trg_room_on_admit
AFTER INSERT ON Admissions
FOR EACH ROW
BEGIN
    UPDATE Rooms SET status = 'Occupied' WHERE room_id = NEW.room_id;
END$$

-- Auto-mark room as Available when patient is discharged
CREATE TRIGGER trg_room_on_discharge
AFTER UPDATE ON Admissions
FOR EACH ROW
BEGIN
    IF NEW.status = 'Discharged' AND OLD.status = 'Admitted' THEN
        UPDATE Rooms SET status = 'Available' WHERE room_id = NEW.room_id;
    END IF;
END$$

DELIMITER ;

-- ============================================================
--  VIEWS
-- ============================================================

-- Full patient appointment history
CREATE OR REPLACE VIEW vw_patient_appointments AS
SELECT
    a.appointment_id,
    CONCAT(p.first_name,' ',p.last_name) AS patient_name,
    CONCAT(d.first_name,' ',d.last_name) AS doctor_name,
    dep.dept_name,
    a.appointment_date,
    a.appointment_time,
    a.reason,
    a.status
FROM Appointments a
JOIN Patients    p   ON a.patient_id = p.patient_id
JOIN Doctors     d   ON a.doctor_id  = d.doctor_id
JOIN Departments dep ON d.dept_id    = dep.dept_id;

-- Current admission status
CREATE OR REPLACE VIEW vw_active_admissions AS
SELECT
    ad.admission_id,
    CONCAT(p.first_name,' ',p.last_name) AS patient_name,
    CONCAT(d.first_name,' ',d.last_name) AS doctor_name,
    r.room_number,
    r.room_type,
    ad.admission_date,
    ad.diagnosis,
    ad.status
FROM Admissions ad
JOIN Patients p ON ad.patient_id = p.patient_id
JOIN Doctors  d ON ad.doctor_id  = d.doctor_id
JOIN Rooms    r ON ad.room_id    = r.room_id
WHERE ad.status = 'Admitted';

-- Billing summary per patient
CREATE OR REPLACE VIEW vw_billing_summary AS
SELECT
    b.bill_id,
    CONCAT(p.first_name,' ',p.last_name) AS patient_name,
    b.bill_date,
    b.consultation_fee,
    b.room_charges,
    b.medicine_charges,
    b.other_charges,
    b.total_amount,
    b.payment_status,
    b.payment_method
FROM Billing b
JOIN Patients p ON b.patient_id = p.patient_id;

-- ============================================================
--  SAMPLE DATA
-- ============================================================

INSERT INTO Departments (dept_name, location, head_doctor) VALUES
('Cardiology',      'Block A, Floor 2', 'Dr. Ramesh Kumar'),
('Neurology',       'Block B, Floor 3', 'Dr. Priya Sharma'),
('Orthopedics',     'Block C, Floor 1', 'Dr. Anil Verma'),
('Pediatrics',      'Block A, Floor 1', 'Dr. Meena Pillai'),
('General Medicine','Block D, Floor 2', 'Dr. Suresh Nair');

INSERT INTO Doctors (first_name, last_name, specialization, phone, email, dept_id, joining_date) VALUES
('Ramesh',  'Kumar',   'Cardiologist',          '9876543210', 'ramesh@lifelinedb.com',  1, '2015-06-01'),
('Priya',   'Sharma',  'Neurologist',            '9876543211', 'priya@lifelinedb.com',   2, '2017-03-15'),
('Anil',    'Verma',   'Orthopedic Surgeon',     '9876543212', 'anil@lifelinedb.com',    3, '2018-09-10'),
('Meena',   'Pillai',  'Pediatrician',           '9876543213', 'meena@lifelinedb.com',   4, '2019-01-20'),
('Suresh',  'Nair',    'General Physician',      '9876543214', 'suresh@lifelinedb.com',  5, '2016-07-05');

INSERT INTO Patients (first_name, last_name, dob, gender, blood_group, phone, email, address, emergency_contact) VALUES
('Arjun',   'Patel',   '1985-04-12', 'Male',   'O+',  '9001112221', 'arjun@email.com',  '12 MG Road, Chennai',    '9001112229'),
('Lakshmi', 'Iyer',    '1992-08-25', 'Female', 'B+',  '9001112222', 'lakshmi@email.com','34 Anna Nagar, Chennai', '9001112228'),
('Karthik', 'Raj',     '1978-11-03', 'Male',   'A-',  '9001112223', 'karthik@email.com','56 T Nagar, Chennai',    '9001112227'),
('Deepa',   'Menon',   '2001-02-17', 'Female', 'AB+', '9001112224', 'deepa@email.com',  '78 Adyar, Chennai',      '9001112226'),
('Vijay',   'Krishnan','1965-07-30', 'Male',   'O-',  '9001112225', 'vijay@email.com',  '90 Velachery, Chennai',  '9001112225');

INSERT INTO Rooms (room_number, room_type, floor, capacity, status, daily_rate) VALUES
('101', 'General',     1, 4, 'Available', 500.00),
('201', 'Semi-Private', 2, 2, 'Available', 1200.00),
('301', 'Private',     3, 1, 'Available', 2500.00),
('401', 'ICU',         4, 1, 'Available', 5000.00),
('102', 'General',     1, 4, 'Available', 500.00);

INSERT INTO Appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status) VALUES
(1, 1, '2025-03-10', '09:00:00', 'Chest pain checkup',       'Completed'),
(2, 2, '2025-03-11', '10:30:00', 'Severe headaches',         'Completed'),
(3, 3, '2025-03-12', '11:00:00', 'Knee pain',                'Completed'),
(4, 4, '2025-03-13', '14:00:00', 'Fever and cold',           'Scheduled'),
(5, 5, '2025-03-14', '15:30:00', 'General health checkup',   'Scheduled');

INSERT INTO Admissions (patient_id, doctor_id, room_id, admission_date, diagnosis, status) VALUES
(1, 1, 4, '2025-03-10', 'Acute myocardial infarction', 'Admitted'),
(2, 2, 3, '2025-03-11', 'Migraine with aura',          'Discharged');

UPDATE Admissions SET discharge_date = '2025-03-14', status = 'Discharged' WHERE admission_id = 2;

INSERT INTO Prescriptions (patient_id, doctor_id, appointment_id, prescribed_date, medicine_name, dosage, duration, instructions) VALUES
(1, 1, 1, '2025-03-10', 'Aspirin 75mg',        '1 tablet daily',   '30 days', 'Take after meals'),
(1, 1, 1, '2025-03-10', 'Atorvastatin 20mg',   '1 tablet at night','60 days', 'Take before sleep'),
(2, 2, 2, '2025-03-11', 'Sumatriptan 50mg',    '1 tablet as needed','15 days','Take at onset of migraine'),
(3, 3, 3, '2025-03-12', 'Ibuprofen 400mg',     '1 tablet thrice daily','10 days','Take with food');

INSERT INTO Billing (patient_id, admission_id, bill_date, consultation_fee, room_charges, medicine_charges, other_charges, payment_status, payment_method) VALUES
(1, 1, '2025-03-10', 1500.00, 20000.00, 3500.00, 1000.00, 'Pending', 'Insurance'),
(2, 2, '2025-03-14', 1200.00,  8000.00, 1200.00,  500.00,  'Paid',   'Card'),
(3, NULL,'2025-03-12', 800.00,     0.00,  600.00,    0.00,  'Paid',   'Cash');
