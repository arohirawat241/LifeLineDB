"""
LifeLineDB — Database Connection & Query Helper
"""
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime
import os

# ── Connection config (edit these or use env vars) ──────────────
DB_CONFIG = {
    "host":     os.getenv("LIFELINEDB_HOST",   "localhost"),
    "port":     int(os.getenv("LIFELINEDB_PORT", 3306)),
    "user":     os.getenv("LIFELINEDB_USER",   "root"),
    "password": os.getenv("LIFELINEDB_PASS",   "arohi241"),
    "database": "LifeLineDB",
    "autocommit": True,
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def execute_query(sql, params=None, fetch=False):
    """Execute a query; returns rows if fetch=True, else lastrowid."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            return cur.fetchall()
        conn.commit()
        return cur.lastrowid
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

# ─────────────────────────────────────────
#  PATIENTS
# ─────────────────────────────────────────
def get_all_patients():
    return execute_query("SELECT * FROM Patients ORDER BY registered_at DESC", fetch=True)

def get_patient(pid):
    return execute_query("SELECT * FROM Patients WHERE patient_id=%s", (pid,), fetch=True)

def add_patient(data):
    sql = """INSERT INTO Patients
             (first_name,last_name,dob,gender,blood_group,phone,email,address,emergency_contact)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    return execute_query(sql, (
        data['first_name'], data['last_name'], data['dob'], data['gender'],
        data['blood_group'], data['phone'], data['email'], data['address'],
        data['emergency_contact']
    ))

def update_patient(pid, data):
    sql = """UPDATE Patients SET first_name=%s,last_name=%s,dob=%s,gender=%s,
             blood_group=%s,phone=%s,email=%s,address=%s,emergency_contact=%s
             WHERE patient_id=%s"""
    execute_query(sql, (
        data['first_name'], data['last_name'], data['dob'], data['gender'],
        data['blood_group'], data['phone'], data['email'], data['address'],
        data['emergency_contact'], pid
    ))

def delete_patient(pid):
    execute_query("DELETE FROM Patients WHERE patient_id=%s", (pid,))

def search_patients(term):
    sql = """SELECT * FROM Patients
             WHERE first_name LIKE %s OR last_name LIKE %s OR phone LIKE %s"""
    t = f"%{term}%"
    return execute_query(sql, (t, t, t), fetch=True)

# ─────────────────────────────────────────
#  DOCTORS
# ─────────────────────────────────────────
def get_all_doctors():
    sql = """SELECT d.*, dept.dept_name FROM Doctors d
             LEFT JOIN Departments dept ON d.dept_id=dept.dept_id
             ORDER BY d.doctor_id"""
    return execute_query(sql, fetch=True)

def add_doctor(data):
    sql = """INSERT INTO Doctors
             (first_name,last_name,specialization,phone,email,dept_id,joining_date)
             VALUES (%s,%s,%s,%s,%s,%s,%s)"""
    return execute_query(sql, (
        data['first_name'], data['last_name'], data['specialization'],
        data['phone'], data['email'], data['dept_id'], data['joining_date']
    ))

def update_doctor(did, data):
    sql = """UPDATE Doctors SET first_name=%s,last_name=%s,specialization=%s,
             phone=%s,email=%s,dept_id=%s WHERE doctor_id=%s"""
    execute_query(sql, (
        data['first_name'], data['last_name'], data['specialization'],
        data['phone'], data['email'], data['dept_id'], did
    ))

def delete_doctor(did):
    execute_query("DELETE FROM Doctors WHERE doctor_id=%s", (did,))

# ─────────────────────────────────────────
#  DEPARTMENTS
# ─────────────────────────────────────────
def get_all_departments():
    return execute_query("SELECT * FROM Departments ORDER BY dept_id", fetch=True)

def add_department(data):
    sql = "INSERT INTO Departments (dept_name,location,head_doctor) VALUES (%s,%s,%s)"
    return execute_query(sql, (data['dept_name'], data['location'], data['head_doctor']))

# ─────────────────────────────────────────
#  APPOINTMENTS
# ─────────────────────────────────────────
def get_all_appointments():
    return execute_query("SELECT * FROM vw_patient_appointments ORDER BY appointment_date DESC", fetch=True)

def add_appointment(data):
    sql = """INSERT INTO Appointments
             (patient_id,doctor_id,appointment_date,appointment_time,reason,status,notes)
             VALUES (%s,%s,%s,%s,%s,%s,%s)"""
    return execute_query(sql, (
        data['patient_id'], data['doctor_id'], data['appointment_date'],
        data['appointment_time'], data['reason'], data['status'], data.get('notes','')
    ))

def update_appointment_status(aid, status):
    execute_query("UPDATE Appointments SET status=%s WHERE appointment_id=%s", (status, aid))

def delete_appointment(aid):
    execute_query("DELETE FROM Appointments WHERE appointment_id=%s", (aid,))

# ─────────────────────────────────────────
#  ROOMS
# ─────────────────────────────────────────
def get_all_rooms():
    return execute_query("SELECT * FROM Rooms ORDER BY room_number", fetch=True)

def get_available_rooms():
    return execute_query("SELECT * FROM Rooms WHERE status='Available' ORDER BY room_type", fetch=True)

def add_room(data):
    sql = """INSERT INTO Rooms (room_number,room_type,floor,capacity,daily_rate)
             VALUES (%s,%s,%s,%s,%s)"""
    return execute_query(sql, (
        data['room_number'], data['room_type'], data['floor'],
        data['capacity'], data['daily_rate']
    ))

# ─────────────────────────────────────────
#  ADMISSIONS
# ─────────────────────────────────────────
def get_active_admissions():
    return execute_query("SELECT * FROM vw_active_admissions", fetch=True)

def get_all_admissions():
    return execute_query("""
        SELECT a.*, CONCAT(p.first_name,' ',p.last_name) AS patient_name,
               CONCAT(d.first_name,' ',d.last_name) AS doctor_name, r.room_number
        FROM Admissions a
        JOIN Patients p ON a.patient_id=p.patient_id
        JOIN Doctors  d ON a.doctor_id=d.doctor_id
        JOIN Rooms    r ON a.room_id=r.room_id
        ORDER BY a.admission_date DESC
    """, fetch=True)

def add_admission(data):
    sql = """INSERT INTO Admissions
             (patient_id,doctor_id,room_id,admission_date,diagnosis,status)
             VALUES (%s,%s,%s,%s,%s,'Admitted')"""
    return execute_query(sql, (
        data['patient_id'], data['doctor_id'], data['room_id'],
        data['admission_date'], data['diagnosis']
    ))

def discharge_patient(admission_id, discharge_date):
    sql = """UPDATE Admissions SET status='Discharged', discharge_date=%s
             WHERE admission_id=%s"""
    execute_query(sql, (discharge_date, admission_id))

# ─────────────────────────────────────────
#  PRESCRIPTIONS
# ─────────────────────────────────────────
def get_prescriptions_for_patient(pid):
    sql = """SELECT pr.*, CONCAT(d.first_name,' ',d.last_name) AS doctor_name
             FROM Prescriptions pr
             JOIN Doctors d ON pr.doctor_id=d.doctor_id
             WHERE pr.patient_id=%s ORDER BY pr.prescribed_date DESC"""
    return execute_query(sql, (pid,), fetch=True)

def get_all_prescriptions():
    sql = """SELECT pr.*, CONCAT(p.first_name,' ',p.last_name) AS patient_name,
                    CONCAT(d.first_name,' ',d.last_name) AS doctor_name
             FROM Prescriptions pr
             JOIN Patients p ON pr.patient_id=p.patient_id
             JOIN Doctors  d ON pr.doctor_id=d.doctor_id
             ORDER BY pr.prescribed_date DESC"""
    return execute_query(sql, fetch=True)

def add_prescription(data):
    sql = """INSERT INTO Prescriptions
             (patient_id,doctor_id,appointment_id,prescribed_date,
              medicine_name,dosage,duration,instructions)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    return execute_query(sql, (
        data['patient_id'], data['doctor_id'], data.get('appointment_id'),
        data['prescribed_date'], data['medicine_name'], data['dosage'],
        data['duration'], data['instructions']
    ))

# ─────────────────────────────────────────
#  BILLING
# ─────────────────────────────────────────
def get_all_bills():
    return execute_query("SELECT * FROM vw_billing_summary ORDER BY bill_date DESC", fetch=True)

def add_bill(data):
    sql = """INSERT INTO Billing
             (patient_id,admission_id,bill_date,consultation_fee,room_charges,
              medicine_charges,other_charges,payment_status,payment_method)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    return execute_query(sql, (
        data['patient_id'], data.get('admission_id'), data['bill_date'],
        data['consultation_fee'], data['room_charges'], data['medicine_charges'],
        data['other_charges'], data['payment_status'], data['payment_method']
    ))

def update_bill_status(bid, status):
    execute_query("UPDATE Billing SET payment_status=%s WHERE bill_id=%s", (status, bid))

# ─────────────────────────────────────────
#  DASHBOARD STATS
# ─────────────────────────────────────────
def get_dashboard_stats():
    stats = {}
    stats['total_patients']    = execute_query("SELECT COUNT(*) AS c FROM Patients", fetch=True)[0]['c']
    stats['total_doctors']     = execute_query("SELECT COUNT(*) AS c FROM Doctors",  fetch=True)[0]['c']
    stats['active_admissions'] = execute_query("SELECT COUNT(*) AS c FROM Admissions WHERE status='Admitted'", fetch=True)[0]['c']
    stats['today_appointments']= execute_query(
        "SELECT COUNT(*) AS c FROM Appointments WHERE appointment_date=CURDATE()", fetch=True)[0]['c']
    stats['available_rooms']   = execute_query("SELECT COUNT(*) AS c FROM Rooms WHERE status='Available'", fetch=True)[0]['c']
    stats['pending_bills']     = execute_query(
        "SELECT COALESCE(SUM(total_amount),0) AS c FROM Billing WHERE payment_status='Pending'", fetch=True)[0]['c']
    return stats
