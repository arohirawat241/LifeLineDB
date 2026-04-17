"""
LifeLineDB — Hospital Management System GUI
Built with Tkinter | Connects to MySQL via backend/db.py
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from backend.db import *
except ImportError:
    from db import *

# ─── Colour Palette ─────────────────────────────────────────────
BG         = "#0D1117"
SIDEBAR_BG = "#161B22"
CARD_BG    = "#1C2128"
ACCENT     = "#00C896"
ACCENT2    = "#0EA5E9"
WARN       = "#F59E0B"
DANGER     = "#EF4444"
TEXT       = "#E6EDF3"
MUTED      = "#7D8590"
BORDER     = "#30363D"
WHITE      = "#FFFFFF"
HEADER_BG  = "#1C2128"

FONT_HEAD  = ("Segoe UI", 22, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO  = ("Consolas", 10)

ICONS = {
    "dashboard":     "⬛",
    "patients":      "👤",
    "doctors":       "🩺",
    "departments":   "🏢",
    "appointments":  "📅",
    "rooms":         "🛏",
    "admissions":    "🏥",
    "prescriptions": "💊",
    "billing":       "💳",
}

# ════════════════════════════════════════════════════════════════
class LifeLineApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LifeLineDB — Hospital Management System")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(bg=BG)

        self._style()
        self._layout()
        self._show("dashboard")

    # ── ttk style ──────────────────────────────────────────────
    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=BG, foreground=TEXT, font=FONT_BODY)
        s.configure("Treeview",
            background=CARD_BG, foreground=TEXT,
            fieldbackground=CARD_BG, rowheight=28,
            font=FONT_BODY, borderwidth=0)
        s.configure("Treeview.Heading",
            background=SIDEBAR_BG, foreground=ACCENT,
            font=("Segoe UI", 10, "bold"), relief="flat")
        s.map("Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", BG)])
        s.configure("TScrollbar", background=BORDER,
            troughcolor=CARD_BG, borderwidth=0, arrowsize=14)
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab",
            background=SIDEBAR_BG, foreground=MUTED,
            padding=[14,6], font=FONT_BODY)
        s.map("TNotebook.Tab",
            background=[("selected", ACCENT)],
            foreground=[("selected", BG)])

    # ── Master layout: sidebar + content ───────────────────────
    def _layout(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(self.sidebar, bg=SIDEBAR_BG, pady=20)
        logo.pack(fill="x")
        tk.Label(logo, text="❤️", font=("Segoe UI", 24), bg=SIDEBAR_BG,
                 fg=ACCENT).pack()
        tk.Label(logo, text="LifeLineDB", font=("Segoe UI", 14, "bold"),
                 bg=SIDEBAR_BG, fg=WHITE).pack()
        tk.Label(logo, text="Hospital Management", font=FONT_SMALL,
                 bg=SIDEBAR_BG, fg=MUTED).pack()

        ttk.Separator(self.sidebar).pack(fill="x", padx=16, pady=6)

        self.nav_btns = {}
        pages = [
            ("dashboard",    "Dashboard"),
            ("patients",     "Patients"),
            ("doctors",      "Doctors"),
            ("departments",  "Departments"),
            ("appointments", "Appointments"),
            ("rooms",        "Rooms"),
            ("admissions",   "Admissions"),
            ("prescriptions","Prescriptions"),
            ("billing",      "Billing"),
        ]
        for key, label in pages:
            btn = tk.Button(
                self.sidebar,
                text=f"  {ICONS[key]}  {label}",
                anchor="w", font=FONT_BODY,
                bg=SIDEBAR_BG, fg=TEXT,
                activebackground=ACCENT, activeforeground=BG,
                bd=0, padx=16, pady=10, cursor="hand2",
                command=lambda k=key: self._show(k)
            )
            btn.pack(fill="x", padx=6, pady=1)
            self.nav_btns[key] = btn

        # Version at bottom
        tk.Label(self.sidebar, text="v1.0  •  MySQL", font=FONT_SMALL,
                 bg=SIDEBAR_BG, fg=MUTED).pack(side="bottom", pady=12)

        # Content area
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.frames = {}

    def _show(self, key):
        for k, btn in self.nav_btns.items():
            btn.config(bg=SIDEBAR_BG if k != key else ACCENT,
                       fg=TEXT       if k != key else BG)

        for f in self.content.winfo_children():
            f.destroy()

        builders = {
            "dashboard":    DashboardFrame,
            "patients":     PatientsFrame,
            "doctors":      DoctorsFrame,
            "departments":  DepartmentsFrame,
            "appointments": AppointmentsFrame,
            "rooms":        RoomsFrame,
            "admissions":   AdmissionsFrame,
            "prescriptions":PrescriptionsFrame,
            "billing":      BillingFrame,
        }
        frame = builders[key](self.content)
        frame.pack(fill="both", expand=True)

# ════════════════════════════════════════════════════════════════
#  REUSABLE HELPERS
# ════════════════════════════════════════════════════════════════
def page_header(parent, title, subtitle=""):
    hdr = tk.Frame(parent, bg=HEADER_BG, pady=18, padx=28)
    hdr.pack(fill="x")
    tk.Label(hdr, text=title, font=FONT_HEAD,
             bg=HEADER_BG, fg=WHITE).pack(anchor="w")
    if subtitle:
        tk.Label(hdr, text=subtitle, font=FONT_SMALL,
                 bg=HEADER_BG, fg=MUTED).pack(anchor="w")

def card(parent, **kwargs):
    f = tk.Frame(parent, bg=CARD_BG, bd=0, **kwargs)
    return f

def stat_card(parent, label, value, color=ACCENT):
    c = tk.Frame(parent, bg=CARD_BG, padx=20, pady=16,
                 highlightbackground=BORDER, highlightthickness=1)
    tk.Label(c, text=str(value), font=("Segoe UI", 26, "bold"),
             bg=CARD_BG, fg=color).pack(anchor="w")
    tk.Label(c, text=label, font=FONT_SMALL,
             bg=CARD_BG, fg=MUTED).pack(anchor="w")
    return c

def action_btn(parent, text, cmd, color=ACCENT, **kw):
    return tk.Button(parent, text=text, command=cmd,
                     bg=color, fg=BG, font=("Segoe UI", 9, "bold"),
                     bd=0, padx=14, pady=6, cursor="hand2",
                     activebackground=WHITE, activeforeground=BG, **kw)

def make_tree(parent, cols, col_widths=None):
    frame = tk.Frame(parent, bg=CARD_BG)
    frame.pack(fill="both", expand=True, padx=16, pady=8)

    tree = ttk.Treeview(frame, columns=cols, show="headings",
                        selectmode="browse")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    for i, c in enumerate(cols):
        w = col_widths[i] if col_widths and i < len(col_widths) else 120
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor="w", minwidth=60)

    vsb.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    hsb.pack(fill="x")
    return tree

def form_field(parent, label, row, col=0, widget_type="entry",
               options=None, width=28, colspan=1):
    tk.Label(parent, text=label, font=FONT_SMALL, bg=CARD_BG,
             fg=MUTED, anchor="w").grid(row=row, column=col*2,
             sticky="w", padx=(12,4), pady=4)
    if widget_type == "entry":
        var = tk.StringVar()
        w = tk.Entry(parent, textvariable=var, width=width,
                     bg=SIDEBAR_BG, fg=TEXT, insertbackground=TEXT,
                     relief="flat", bd=6, font=FONT_BODY)
        w.grid(row=row, column=col*2+1, sticky="ew", padx=(0,12), pady=4,
               columnspan=colspan)
        return var, w
    elif widget_type == "combo":
        var = tk.StringVar()
        w = ttk.Combobox(parent, textvariable=var, values=options or [],
                         state="readonly", width=width-3, font=FONT_BODY)
        w.grid(row=row, column=col*2+1, sticky="ew", padx=(0,12), pady=4,
               columnspan=colspan)
        return var, w
    elif widget_type == "text":
        w = tk.Text(parent, width=width, height=3,
                    bg=SIDEBAR_BG, fg=TEXT, insertbackground=TEXT,
                    relief="flat", bd=6, font=FONT_BODY)
        w.grid(row=row, column=col*2+1, sticky="ew", padx=(0,12), pady=4,
               columnspan=colspan)
        return w, w

def db_error(e):
    messagebox.showerror("Database Error", str(e))

# ════════════════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════════════════
class DashboardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        page_header(self, "Dashboard", f"Welcome back  •  {date.today().strftime('%B %d, %Y')}")
        self._build()

    def _build(self):
        try:
            stats = get_dashboard_stats()
        except Exception as e:
            tk.Label(self, text=f"⚠️  Could not connect to database.\n{e}",
                     font=FONT_BODY, bg=BG, fg=DANGER, justify="left",
                     padx=28, pady=20).pack(anchor="w")
            return

        grid = tk.Frame(self, bg=BG, padx=24, pady=16)
        grid.pack(fill="x")

        items = [
            ("Total Patients",     stats['total_patients'],    ACCENT),
            ("Doctors",            stats['total_doctors'],     ACCENT2),
            ("Active Admissions",  stats['active_admissions'], WARN),
            ("Today's Appointments", stats['today_appointments'], "#A78BFA"),
            ("Available Rooms",    stats['available_rooms'],   ACCENT),
            ("Pending Bills (₹)",  f"{stats['pending_bills']:,.2f}", DANGER),
        ]
        for i, (lbl, val, col) in enumerate(items):
            c = stat_card(grid, lbl, val, col)
            c.grid(row=i//3, column=i%3, sticky="nsew", padx=8, pady=8)
        for i in range(3):
            grid.columnconfigure(i, weight=1)

        # Recent appointments
        tk.Label(self, text="Recent Appointments", font=FONT_TITLE,
         bg=BG, fg=WHITE, padx=24, pady=12).pack(anchor="w")
        cols = ("Patient", "Doctor", "Department", "Date", "Time", "Status")
        tree = make_tree(self, cols, [180,160,140,100,80,100])
        try:
            rows = get_all_appointments()[:10]
            for r in rows:
                s = r['status']
                tag = "completed" if s == "Completed" else "cancelled" if s == "Cancelled" else ""
                tree.insert("", "end", values=(
                    r['patient_name'], r['doctor_name'], r['dept_name'],
                    str(r['appointment_date']), str(r['appointment_time'])[:5], s
                ), tags=(tag,))
            tree.tag_configure("completed", foreground=ACCENT)
            tree.tag_configure("cancelled", foreground=DANGER)
        except Exception as e:
            db_error(e)

# ════════════════════════════════════════════════════════════════
#  PATIENTS
# ════════════════════════════════════════════════════════════════
class PatientsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        page_header(self, "👤  Patient Management", "Add, edit, search and manage patients")
        self._selected_id = None
        self._build()
        self._load()

    def _build(self):
        # Toolbar
        bar = tk.Frame(self, bg=BG, padx=16, pady=8)
        bar.pack(fill="x")
        self.search_var = tk.StringVar()
        se = tk.Entry(bar, textvariable=self.search_var, width=30,
                      bg=CARD_BG, fg=TEXT, insertbackground=TEXT,
                      relief="flat", bd=6, font=FONT_BODY)
        se.pack(side="left", padx=(0,8))
        se.insert(0, "🔍  Search patients...")
        se.bind("<FocusIn>",  lambda e: se.delete(0,"end") if se.get().startswith("🔍") else None)
        se.bind("<Return>",   lambda e: self._search())
        action_btn(bar, "Search", self._search).pack(side="left", padx=4)
        action_btn(bar, "+ Add Patient", self._open_add, color=ACCENT2).pack(side="right")
        action_btn(bar, "✏ Edit",    self._edit,   color=WARN).pack(side="right", padx=4)
        action_btn(bar, "🗑 Delete", self._delete, color=DANGER).pack(side="right")

        cols = ("ID","First Name","Last Name","DOB","Gender","Blood","Phone","Email")
        self.tree = make_tree(self, cols, [40,110,110,90,70,60,110,160])

    def _load(self, rows=None):
        self.tree.delete(*self.tree.get_children())
        try:
            data = rows if rows is not None else get_all_patients()
            for r in data:
                self.tree.insert("", "end", iid=r['patient_id'], values=(
                    r['patient_id'], r['first_name'], r['last_name'],
                    str(r['dob']), r['gender'], r['blood_group'],
                    r['phone'], r['email'] or ""
                ))
        except Exception as e:
            db_error(e)

    def _search(self):
        t = self.search_var.get().strip()
        if not t or t.startswith("🔍"):
            self._load(); return
        try:
            self._load(search_patients(t))
        except Exception as e:
            db_error(e)

    def _selected(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _open_add(self, pid=None):
        win = PatientFormWindow(self, pid)
        self.wait_window(win)
        self._load()

    def _edit(self):
        pid = self._selected()
        if not pid: messagebox.showwarning("Select","Please select a patient first."); return
        self._open_add(pid)

    def _delete(self):
        pid = self._selected()
        if not pid: messagebox.showwarning("Select","Please select a patient first."); return
        if messagebox.askyesno("Confirm","Delete this patient? All related records will be removed."):
            try:
                delete_patient(pid)
                self._load()
            except Exception as e:
                db_error(e)


class PatientFormWindow(tk.Toplevel):
    def __init__(self, parent, pid=None):
        super().__init__(parent)
        self.pid = pid
        self.title("Edit Patient" if pid else "Add New Patient")
        self.configure(bg=CARD_BG)
        self.resizable(False, False)
        self._build()
        if pid:
            self._prefill()

    def _build(self):
        tk.Label(self, text="Patient Details", font=FONT_TITLE,
                 bg=CARD_BG, fg=WHITE, pady=12).grid(row=0, columnspan=4, padx=12)

        self.v_fn,  _ = form_field(self, "First Name*", 1, 0)
        self.v_ln,  _ = form_field(self, "Last Name*",  1, 1)
        self.v_dob, _ = form_field(self, "Date of Birth (YYYY-MM-DD)", 2, 0)
        self.v_gen, _ = form_field(self, "Gender", 2, 1, "combo",
                                   ["Male","Female","Other"])
        self.v_bg,  _ = form_field(self, "Blood Group", 3, 0, "combo",
                                   ["A+","A-","B+","B-","AB+","AB-","O+","O-"])
        self.v_ph,  _ = form_field(self, "Phone*", 3, 1)
        self.v_em,  _ = form_field(self, "Email",  4, 0)
        self.v_ec,  _ = form_field(self, "Emergency Contact", 4, 1)
        self.w_addr,_ = form_field(self, "Address", 5, 0, "text", colspan=3)

        bf = tk.Frame(self, bg=CARD_BG, pady=12)
        bf.grid(row=6, columnspan=4)
        action_btn(bf, "💾 Save", self._save).pack(side="left", padx=8)
        tk.Button(bf, text="Cancel", command=self.destroy,
                  bg=BORDER, fg=TEXT, bd=0, padx=14, pady=6,
                  cursor="hand2").pack(side="left")

        for i in range(4): self.columnconfigure(i, weight=1)

    def _prefill(self):
        try:
            r = get_patient(self.pid)[0]
            self.v_fn.set(r['first_name']); self.v_ln.set(r['last_name'])
            self.v_dob.set(str(r['dob'])); self.v_gen.set(r['gender'] or "")
            self.v_bg.set(r['blood_group'] or ""); self.v_ph.set(r['phone'] or "")
            self.v_em.set(r['email'] or ""); self.v_ec.set(r['emergency_contact'] or "")
            self.w_addr.insert("1.0", r['address'] or "")
        except Exception as e:
            db_error(e)

    def _save(self):
        data = {
            'first_name':        self.v_fn.get().strip(),
            'last_name':         self.v_ln.get().strip(),
            'dob':               self.v_dob.get().strip() or None,
            'gender':            self.v_gen.get(),
            'blood_group':       self.v_bg.get(),
            'phone':             self.v_ph.get().strip(),
            'email':             self.v_em.get().strip() or None,
            'address':           self.w_addr.get("1.0","end").strip(),
            'emergency_contact': self.v_ec.get().strip() or None,
        }
        if not data['first_name'] or not data['last_name'] or not data['phone']:
            messagebox.showwarning("Required","First name, last name and phone are required."); return
        try:
            if self.pid:
                update_patient(self.pid, data)
            else:
                add_patient(data)
            messagebox.showinfo("Saved","Patient saved successfully.")
            self.destroy()
        except Exception as e:
            db_error(e)

# ════════════════════════════════════════════════════════════════
#  DOCTORS
# ════════════════════════════════════════════════════════════════
class DoctorsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        page_header(self, "🩺  Doctor Management")
        self._build(); self._load()

    def _build(self):
        bar = tk.Frame(self, bg=BG, padx=16, pady=8)
        bar.pack(fill="x")
        action_btn(bar, "+ Add Doctor", self._add, color=ACCENT2).pack(side="right")
        action_btn(bar, "🗑 Delete",   self._delete, color=DANGER).pack(side="right", padx=4)

        cols = ("ID","First Name","Last Name","Specialization","Phone","Email","Department")
        self.tree = make_tree(self, cols, [40,110,110,160,110,160,130])

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        try:
            for r in get_all_doctors():
                self.tree.insert("","end", iid=r['doctor_id'], values=(
                    r['doctor_id'], r['first_name'], r['last_name'],
                    r['specialization'] or "", r['phone'] or "",
                    r['email'] or "", r.get('dept_name') or "—"
                ))
        except Exception as e: db_error(e)

    def _add(self):
        win = DoctorFormWindow(self)
        self.wait_window(win); self._load()

    def _delete(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Select","Select a doctor first."); return
        did = int(sel[0])
        if messagebox.askyesno("Confirm","Delete this doctor?"):
            try: delete_doctor(did); self._load()
            except Exception as e: db_error(e)


class DoctorFormWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Doctor"); self.configure(bg=CARD_BG); self.resizable(False,False)
        try:
            self.depts = get_all_departments()
            self.dept_names = [d['dept_name'] for d in self.depts]
        except: self.depts = []; self.dept_names = []
        self._build()

    def _build(self):
        tk.Label(self, text="Doctor Details", font=FONT_TITLE,
                 bg=CARD_BG, fg=WHITE, pady=12).grid(row=0, columnspan=4, padx=12)
        self.v_fn,_  = form_field(self,"First Name*",  1,0)
        self.v_ln,_  = form_field(self,"Last Name*",   1,1)
        self.v_sp,_  = form_field(self,"Specialization",2,0)
        self.v_ph,_  = form_field(self,"Phone",        2,1)
        self.v_em,_  = form_field(self,"Email",        3,0)
        self.v_jd,_  = form_field(self,"Joining Date", 3,1)
        self.v_dp,_  = form_field(self,"Department",   4,0,"combo",self.dept_names)

        bf = tk.Frame(self, bg=CARD_BG, pady=12); bf.grid(row=5, columnspan=4)
        action_btn(bf,"💾 Save", self._save).pack(side="left", padx=8)
        tk.Button(bf,"Cancel",command=self.destroy,
                  bg=BORDER,fg=TEXT,bd=0,padx=14,pady=6,cursor="hand2").pack(side="left")
        for i in range(4): self.columnconfigure(i,weight=1)

    def _save(self):
        dept_id = None
        dn = self.v_dp.get()
        for d in self.depts:
            if d['dept_name'] == dn: dept_id = d['dept_id']; break
        data = {
            'first_name':    self.v_fn.get().strip(),
            'last_name':     self.v_ln.get().strip(),
            'specialization':self.v_sp.get().strip(),
            'phone':         self.v_ph.get().strip() or None,
            'email':         self.v_em.get().strip() or None,
            'dept_id':       dept_id,
            'joining_date':  self.v_jd.get().strip() or None,
        }
        if not data['first_name'] or not data['last_name']:
            messagebox.showwarning("Required","Name is required."); return
        try:
            add_doctor(data)
            messagebox.showinfo("Saved","Doctor added.")
            self.destroy()
        except Exception as e: db_error(e)

# ════════════════════════════════════════════════════════════════
#  DEPARTMENTS
# ════════════════════════════════════════════════════════════════
class DepartmentsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        page_header(self, "🏢  Departments")
        self._build(); self._load()

    def _build(self):
        bar = tk.Frame(self, bg=BG, padx=16, pady=8); bar.pack(fill="x")
        action_btn(bar,"+ Add Department",self._add,color=ACCENT2).pack(side="right")
        cols = ("ID","Department Name","Location","Head Doctor")
        self.tree = make_tree(self, cols, [40,200,200,200])

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        try:
            for r in get_all_departments():
                self.tree.insert("","end", values=(
                    r['dept_id'], r['dept_name'],
                    r['location'] or "—", r['head_doctor'] or "—"
                ))
        except Exception as e: db_error(e)

    def _add(self):
        win = tk.Toplevel(self); win.title("Add Department")
        win.configure(bg=CARD_BG); win.resizable(False,False)
        v_dn,_ = form_field(win,"Department Name*",0,0)
        v_lo,_ = form_field(win,"Location",        1,0)
        v_hd,_ = form_field(win,"Head Doctor",     2,0)
        def save():
            if not v_dn.get().strip():
                messagebox.showwarning("Required","Name required."); return
            try:
                add_department({'dept_name':v_dn.get().strip(),
                                'location':v_lo.get().strip(),
                                'head_doctor':v_hd.get().strip()})
                messagebox.showinfo("Saved","Department added.")
                win.destroy(); self._load()
            except Exception as e: db_error(e)
        action_btn(win,"💾 Save",save).grid(row=3,columnspan=2,pady=12)

# ════════════════════════════════════════════════════════════════
#  APPOINTMENTS
# ════════════════════════════════════════════════════════════════
class AppointmentsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        page_header(self,"📅  Appointments")
        self._build(); self._load()

    def _build(self):
        bar = tk.Frame(self, bg=BG, padx=16, pady=8); bar.pack(fill="x")
        action_btn(bar,"+ New Appointment",self._add,color=ACCENT2).pack(side="right")
        action_btn(bar,"✔ Mark Complete",self._complete,color=ACCENT).pack(side="right",padx=4)
        action_btn(bar,"✖ Cancel",self._cancel,color=DANGER).pack(side="right")
        cols = ("ID","Patient","Doctor","Department","Date","Time","Reason","Status")
        self.tree = make_tree(self, cols, [40,150,130,130,90,60,180,90])

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        try:
            for r in get_all_appointments():
                s = r['status']
                tag = "done" if s=="Completed" else "cancel" if s=="Cancelled" else ""
                self.tree.insert("","end", iid=r['appointment_id'], values=(
                    r['appointment_id'],r['patient_name'],r['doctor_name'],
                    r['dept_name'],str(r['appointment_date']),
                    str(r['appointment_time'])[:5],
                    (r['reason'] or "")[:40], s
                ), tags=(tag,))
            self.tree.tag_configure("done",   foreground=ACCENT)
            self.tree.tag_configure("cancel", foreground=DANGER)
        except Exception as e: db_error(e)

    def _selected_id(self):
        s = self.tree.selection()
        return int(s[0]) if s else None

    def _add(self):
        win = AppointmentFormWindow(self)
        self.wait_window(win); self._load()

    def _complete(self):
        aid = self._selected_id()
        if not aid: messagebox.showwarning("Select","Select an appointment."); return
        try: update_appointment_status(aid,"Completed"); self._load()
        except Exception as e: db_error(e)

    def _cancel(self):
        aid = self._selected_id()
        if not aid: messagebox.showwarning("Select","Select an appointment."); return
        try: update_appointment_status(aid,"Cancelled"); self._load()
        except Exception as e: db_error(e)


class AppointmentFormWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("New Appointment"); self.configure(bg=CARD_BG); self.resizable(False,False)
        try:
            self.patients = get_all_patients()
            self.doctors  = get_all_doctors()
        except: self.patients=[]; self.doctors=[]
        self.p_map = {f"{p['first_name']} {p['last_name']} (#{p['patient_id']})": p['patient_id']
                      for p in self.patients}
        self.d_map = {f"Dr. {d['first_name']} {d['last_name']}": d['doctor_id']
                      for d in self.doctors}
        self._build()

    def _build(self):
        tk.Label(self,text="Book Appointment",font=FONT_TITLE,
                 bg=CARD_BG,fg=WHITE,pady=12).grid(row=0,columnspan=4,padx=12)
        self.v_pt,_ = form_field(self,"Patient*",   1,0,"combo",list(self.p_map.keys()))
        self.v_dr,_ = form_field(self,"Doctor*",    1,1,"combo",list(self.d_map.keys()))
        self.v_dt,_ = form_field(self,"Date (YYYY-MM-DD)*",2,0)
        self.v_tm,_ = form_field(self,"Time (HH:MM)*",     2,1)
        self.w_rs,_ = form_field(self,"Reason",    3,0,"text",colspan=3)

        bf = tk.Frame(self,bg=CARD_BG,pady=12); bf.grid(row=4,columnspan=4)
        action_btn(bf,"💾 Save",self._save).pack(side="left",padx=8)
        tk.Button(bf,"Cancel",command=self.destroy,
                  bg=BORDER,fg=TEXT,bd=0,padx=14,pady=6,cursor="hand2").pack(side="left")
        for i in range(4): self.columnconfigure(i,weight=1)

    def _save(self):
        pid = self.p_map.get(self.v_pt.get())
        did = self.d_map.get(self.v_dr.get())
        if not pid or not did or not self.v_dt.get() or not self.v_tm.get():
            messagebox.showwarning("Required","Patient, doctor, date and time are required."); return
        try:
            add_appointment({'patient_id':pid,'doctor_id':did,
                             'appointment_date':self.v_dt.get(),
                             'appointment_time':self.v_tm.get()+":00",
                             'reason':self.w_rs.get("1.0","end").strip(),
                             'status':'Scheduled'})
            messagebox.showinfo("Saved","Appointment booked.")
            self.destroy()
        except Exception as e: db_error(e)

# ════════════════════════════════════════════════════════════════
#  ROOMS
# ════════════════════════════════════════════════════════════════
class RoomsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        page_header(self,"🛏  Room Management")
        self._build(); self._load()

    def _build(self):
        bar = tk.Frame(self,bg=BG,padx=16,pady=8); bar.pack(fill="x")
        action_btn(bar,"+ Add Room",self._add,color=ACCENT2).pack(side="right")
        cols = ("ID","Room No","Type","Floor","Capacity","Status","Daily Rate (₹)")
        self.tree = make_tree(self,cols,[40,80,120,60,80,100,120])

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        try:
            for r in get_all_rooms():
                tag = "avail" if r['status']=="Available" else "occ" if r['status']=="Occupied" else "maint"
                self.tree.insert("","end",values=(
                    r['room_id'],r['room_number'],r['room_type'],
                    r['floor'],r['capacity'],r['status'],
                    f"₹{r['daily_rate']:,.2f}"
                ),tags=(tag,))
            self.tree.tag_configure("avail", foreground=ACCENT)
            self.tree.tag_configure("occ",   foreground=DANGER)
            self.tree.tag_configure("maint", foreground=WARN)
        except Exception as e: db_error(e)

    def _add(self):
        win = tk.Toplevel(self); win.title("Add Room")
        win.configure(bg=CARD_BG); win.resizable(False,False)
        v_rn,_= form_field(win,"Room Number*",0,0)
        v_rt,_= form_field(win,"Room Type",   0,1,"combo",["General","ICU","Private","Semi-Private"])
        v_fl,_= form_field(win,"Floor",       1,0)
        v_cap,_=form_field(win,"Capacity",    1,1)
        v_rate,_=form_field(win,"Daily Rate*",2,0)
        def save():
            if not v_rn.get() or not v_rate.get():
                messagebox.showwarning("Required","Room number and rate required."); return
            try:
                add_room({'room_number':v_rn.get().strip(),'room_type':v_rt.get() or "General",
                          'floor':int(v_fl.get() or 1),'capacity':int(v_cap.get() or 1),
                          'daily_rate':float(v_rate.get())})
                messagebox.showinfo("Saved","Room added.")
                win.destroy(); self._load()
            except Exception as e: db_error(e)
        action_btn(win,"💾 Save",save).grid(row=3,columnspan=4,pady=12)
        for i in range(4): win.columnconfigure(i,weight=1)

# ════════════════════════════════════════════════════════════════
#  ADMISSIONS
# ════════════════════════════════════════════════════════════════
class AdmissionsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        page_header(self,"🏥  Admissions & Room Allocation")
        self._build(); self._load()

    def _build(self):
        bar = tk.Frame(self,bg=BG,padx=16,pady=8); bar.pack(fill="x")
        action_btn(bar,"+ Admit Patient",self._add,color=ACCENT2).pack(side="right")
        action_btn(bar,"🚪 Discharge",self._discharge,color=WARN).pack(side="right",padx=4)
        cols = ("ID","Patient","Doctor","Room","Admission Date","Diagnosis","Status")
        self.tree = make_tree(self,cols,[40,150,130,70,110,200,90])

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        try:
            for r in get_all_admissions():
                tag = "adm" if r['status']=="Admitted" else "dis"
                self.tree.insert("","end",iid=r['admission_id'],values=(
                    r['admission_id'],r['patient_name'],r['doctor_name'],
                    r['room_number'],str(r['admission_date']),
                    (r['diagnosis'] or "")[:50],r['status']
                ),tags=(tag,))
            self.tree.tag_configure("adm",foreground=WARN)
            self.tree.tag_configure("dis",foreground=ACCENT)
        except Exception as e: db_error(e)

    def _add(self):
        win = AdmissionFormWindow(self)
        self.wait_window(win); self._load()

    def _discharge(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Select","Select an admission."); return
        aid = int(sel[0])
        d = simpledialog.askstring("Discharge Date","Enter discharge date (YYYY-MM-DD):",
                                   initialvalue=str(date.today()))
        if d:
            try: discharge_patient(aid,d); self._load()
            except Exception as e: db_error(e)


class AdmissionFormWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Admit Patient"); self.configure(bg=CARD_BG); self.resizable(False,False)
        try:
            self.patients = get_all_patients()
            self.doctors  = get_all_doctors()
            self.rooms    = get_available_rooms()
        except: self.patients=[]; self.doctors=[]; self.rooms=[]
        self.p_map = {f"{p['first_name']} {p['last_name']} (#{p['patient_id']})": p['patient_id']
                      for p in self.patients}
        self.d_map = {f"Dr. {d['first_name']} {d['last_name']}": d['doctor_id']
                      for d in self.doctors}
        self.r_map = {f"{r['room_number']} – {r['room_type']}": r['room_id']
                      for r in self.rooms}
        self._build()

    def _build(self):
        tk.Label(self,text="Admit Patient",font=FONT_TITLE,
                 bg=CARD_BG,fg=WHITE,pady=12).grid(row=0,columnspan=4,padx=12)
        self.v_pt,_=form_field(self,"Patient*",  1,0,"combo",list(self.p_map.keys()))
        self.v_dr,_=form_field(self,"Doctor*",   1,1,"combo",list(self.d_map.keys()))
        self.v_rm,_=form_field(self,"Room*",     2,0,"combo",list(self.r_map.keys()))
        self.v_dt,_=form_field(self,"Admission Date*",2,1)
        self.v_dt.set(str(date.today()))
        self.w_dg,_=form_field(self,"Diagnosis",3,0,"text",colspan=3)

        bf = tk.Frame(self,bg=CARD_BG,pady=12); bf.grid(row=4,columnspan=4)
        action_btn(bf,"💾 Admit",self._save).pack(side="left",padx=8)
        tk.Button(bf,"Cancel",command=self.destroy,
                  bg=BORDER,fg=TEXT,bd=0,padx=14,pady=6,cursor="hand2").pack(side="left")
        for i in range(4): self.columnconfigure(i,weight=1)

    def _save(self):
        pid = self.p_map.get(self.v_pt.get())
        did = self.d_map.get(self.v_dr.get())
        rid = self.r_map.get(self.v_rm.get())
        if not pid or not did or not rid:
            messagebox.showwarning("Required","Patient, doctor and room are required."); return
        try:
            add_admission({'patient_id':pid,'doctor_id':did,'room_id':rid,
                           'admission_date':self.v_dt.get(),
                           'diagnosis':self.w_dg.get("1.0","end").strip()})
            messagebox.showinfo("Admitted","Patient admitted successfully.")
            self.destroy()
        except Exception as e: db_error(e)

# ════════════════════════════════════════════════════════════════
#  PRESCRIPTIONS
# ════════════════════════════════════════════════════════════════
class PrescriptionsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        page_header(self,"💊  Prescriptions")
        self._build(); self._load()

    def _build(self):
        bar = tk.Frame(self,bg=BG,padx=16,pady=8); bar.pack(fill="x")
        action_btn(bar,"+ Add Prescription",self._add,color=ACCENT2).pack(side="right")
        cols = ("ID","Patient","Doctor","Medicine","Dosage","Duration","Date")
        self.tree = make_tree(self,cols,[40,150,130,180,120,100,90])

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        try:
            for r in get_all_prescriptions():
                self.tree.insert("","end",values=(
                    r['prescription_id'],r['patient_name'],r['doctor_name'],
                    r['medicine_name'],r['dosage'] or "",
                    r['duration'] or "",str(r['prescribed_date'])
                ))
        except Exception as e: db_error(e)

    def _add(self):
        win = PrescriptionFormWindow(self)
        self.wait_window(win); self._load()


class PrescriptionFormWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Prescription"); self.configure(bg=CARD_BG); self.resizable(False,False)
        try:
            self.patients = get_all_patients()
            self.doctors  = get_all_doctors()
        except: self.patients=[]; self.doctors=[]
        self.p_map = {f"{p['first_name']} {p['last_name']} (#{p['patient_id']})": p['patient_id']
                      for p in self.patients}
        self.d_map = {f"Dr. {d['first_name']} {d['last_name']}": d['doctor_id']
                      for d in self.doctors}
        self._build()

    def _build(self):
        tk.Label(self,text="Prescription",font=FONT_TITLE,
                 bg=CARD_BG,fg=WHITE,pady=12).grid(row=0,columnspan=4,padx=12)
        self.v_pt,_=form_field(self,"Patient*",   1,0,"combo",list(self.p_map.keys()))
        self.v_dr,_=form_field(self,"Doctor*",    1,1,"combo",list(self.d_map.keys()))
        self.v_dt,_=form_field(self,"Date*",      2,0)
        self.v_dt.set(str(date.today()))
        self.v_mn,_=form_field(self,"Medicine*",  2,1)
        self.v_ds,_=form_field(self,"Dosage",     3,0)
        self.v_du,_=form_field(self,"Duration",   3,1)
        self.w_in,_=form_field(self,"Instructions",4,0,"text",colspan=3)

        bf = tk.Frame(self,bg=CARD_BG,pady=12); bf.grid(row=5,columnspan=4)
        action_btn(bf,"💾 Save",self._save).pack(side="left",padx=8)
        tk.Button(bf,"Cancel",command=self.destroy,
                  bg=BORDER,fg=TEXT,bd=0,padx=14,pady=6,cursor="hand2").pack(side="left")
        for i in range(4): self.columnconfigure(i,weight=1)

    def _save(self):
        pid = self.p_map.get(self.v_pt.get())
        did = self.d_map.get(self.v_dr.get())
        mn  = self.v_mn.get().strip()
        if not pid or not did or not mn:
            messagebox.showwarning("Required","Patient, doctor and medicine required."); return
        try:
            add_prescription({'patient_id':pid,'doctor_id':did,
                              'prescribed_date':self.v_dt.get(),
                              'medicine_name':mn,'dosage':self.v_ds.get(),
                              'duration':self.v_du.get(),
                              'instructions':self.w_in.get("1.0","end").strip()})
            messagebox.showinfo("Saved","Prescription saved.")
            self.destroy()
        except Exception as e: db_error(e)

# ════════════════════════════════════════════════════════════════
#  BILLING
# ════════════════════════════════════════════════════════════════
class BillingFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        page_header(self,"💳  Billing Management")
        self._build(); self._load()

    def _build(self):
        bar = tk.Frame(self,bg=BG,padx=16,pady=8); bar.pack(fill="x")
        action_btn(bar,"+ Create Bill",self._add,color=ACCENT2).pack(side="right")
        action_btn(bar,"✔ Mark Paid",self._paid,color=ACCENT).pack(side="right",padx=4)
        cols = ("ID","Patient","Date","Consult","Room","Medicine","Other","Total","Status","Method")
        self.tree = make_tree(self,cols,[40,150,90,80,80,80,70,90,80,80])

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        try:
            for r in get_all_bills():
                tag = "paid" if r['payment_status']=="Paid" else "pend"
                self.tree.insert("","end",iid=r['bill_id'],values=(
                    r['bill_id'],r['patient_name'],str(r['bill_date']),
                    f"₹{r['consultation_fee']:,.0f}",f"₹{r['room_charges']:,.0f}",
                    f"₹{r['medicine_charges']:,.0f}",f"₹{r['other_charges']:,.0f}",
                    f"₹{r['total_amount']:,.0f}",r['payment_status'],r['payment_method']
                ),tags=(tag,))
            self.tree.tag_configure("paid",foreground=ACCENT)
            self.tree.tag_configure("pend",foreground=WARN)
        except Exception as e: db_error(e)

    def _add(self):
        win = BillFormWindow(self)
        self.wait_window(win); self._load()

    def _paid(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Select","Select a bill."); return
        try: update_bill_status(int(sel[0]),"Paid"); self._load()
        except Exception as e: db_error(e)


class BillFormWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Bill"); self.configure(bg=CARD_BG); self.resizable(False,False)
        try: self.patients = get_all_patients()
        except: self.patients=[]
        self.p_map={f"{p['first_name']} {p['last_name']} (#{p['patient_id']})": p['patient_id']
                    for p in self.patients}
        self._build()

    def _build(self):
        tk.Label(self,text="Create Bill",font=FONT_TITLE,
                 bg=CARD_BG,fg=WHITE,pady=12).grid(row=0,columnspan=4,padx=12)
        self.v_pt,_=form_field(self,"Patient*",   1,0,"combo",list(self.p_map.keys()))
        self.v_dt,_=form_field(self,"Bill Date*", 1,1)
        self.v_dt.set(str(date.today()))
        self.v_cf,_=form_field(self,"Consultation Fee",2,0)
        self.v_rc,_=form_field(self,"Room Charges",    2,1)
        self.v_mc,_=form_field(self,"Medicine Charges",3,0)
        self.v_oc,_=form_field(self,"Other Charges",   3,1)
        self.v_ps,_=form_field(self,"Payment Status",  4,0,"combo",["Pending","Paid","Partial"])
        self.v_pm,_=form_field(self,"Payment Method",  4,1,"combo",["Cash","Card","Insurance","Online"])

        bf = tk.Frame(self,bg=CARD_BG,pady=12); bf.grid(row=5,columnspan=4)
        action_btn(bf,"💾 Save",self._save).pack(side="left",padx=8)
        tk.Button(bf,"Cancel",command=self.destroy,
                  bg=BORDER,fg=TEXT,bd=0,padx=14,pady=6,cursor="hand2").pack(side="left")
        for i in range(4): self.columnconfigure(i,weight=1)

    def _save(self):
        pid = self.p_map.get(self.v_pt.get())
        if not pid: messagebox.showwarning("Required","Patient required."); return
        try:
            add_bill({'patient_id':pid,'bill_date':self.v_dt.get(),
                      'consultation_fee':float(self.v_cf.get() or 0),
                      'room_charges':    float(self.v_rc.get() or 0),
                      'medicine_charges':float(self.v_mc.get() or 0),
                      'other_charges':   float(self.v_oc.get() or 0),
                      'payment_status':  self.v_ps.get() or "Pending",
                      'payment_method':  self.v_pm.get() or "Cash"})
            messagebox.showinfo("Saved","Bill created.")
            self.destroy()
        except Exception as e: db_error(e)

# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = LifeLineApp()
    app.mainloop()
