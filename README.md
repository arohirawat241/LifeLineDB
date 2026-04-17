# LifeLineDB — Hospital Management System

A relational database-driven healthcare management system built with **MySQL** and **Python (Tkinter)**.

---

## Project Structure

```
LifeLineDB/
├── database/
│   └── schema.sql          ← MySQL schema, triggers, views, sample data
├── backend/
│   └── db.py               ← All database operations (CRUD)
├── gui/
│   └── app.py              ← Tkinter GUI application
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- **Python 3.8+**
- **MySQL 8.0+** running locally

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up the database
Open MySQL and run:
```sql
SOURCE /path/to/LifeLineDB/database/schema.sql;
```
Or via terminal:
```bash
mysql -u root -p < database/schema.sql
```

### 4. Configure database credentials
Edit `backend/db.py` — change the `DB_CONFIG` block:
```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "your_password",
    "database": "LifeLineDB",
}
```
Or use environment variables:
```bash
export LIFELINEDB_USER=root
export LIFELINEDB_PASS=yourpassword
```

### 5. Launch the GUI
```bash
python gui/app.py
```

---

## Database Schema

| Table           | Description                              |
|----------------|------------------------------------------|
| `Departments`   | Hospital departments                     |
| `Doctors`       | Doctor records linked to departments     |
| `Patients`      | Patient demographics & contact info      |
| `Rooms`         | Room inventory with type and daily rate  |
| `Appointments`  | Scheduled/completed patient appointments |
| `Admissions`    | Inpatient stays and room allocation      |
| `Prescriptions` | Medicines, dosage, and instructions      |
| `Billing`       | Itemized bills with payment tracking     |

### Views
- `vw_patient_appointments` — joined appointment history
- `vw_active_admissions`    — currently admitted patients
- `vw_billing_summary`      — billing overview per patient

### Triggers
- `trg_room_on_admit`     — auto-marks room **Occupied** on admission
- `trg_room_on_discharge` — auto-marks room **Available** on discharge

---

## GUI Modules

| Screen          | Features                                           |
|----------------|----------------------------------------------------|
| Dashboard       | Live stats cards + recent appointment table        |
| Patients        | Full CRUD, search by name/phone                    |
| Doctors         | Add/delete, linked to departments                  |
| Departments     | Add and view departments                           |
| Appointments    | Book, mark complete/cancelled                      |
| Rooms           | Add rooms, colour-coded availability               |
| Admissions      | Admit & discharge patients, triggers room status   |
| Prescriptions   | Add prescriptions linked to patient + doctor       |
| Billing         | Create bills, mark as paid                         |

---

##  Technology Stack

| Layer      | Technology            |
|------------|-----------------------|
| Database   | MySQL 8.0             |
| Backend    | Python 3 + mysql-connector |
| GUI        | Tkinter               |
| Queries    | SQL (DDL, DML, Views, Triggers) |

---

##  Notes
- The system uses **3NF normalization** throughout
- Generated column `total_amount` in `Billing` is auto-computed by MySQL
- All foreign keys use `ON DELETE CASCADE` or `ON DELETE SET NULL` as appropriate
- Sample data for 5 patients, 5 doctors, 5 rooms, and related records is included

