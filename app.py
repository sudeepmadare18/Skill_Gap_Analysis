import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import date

st.set_page_config(page_title="Skill Bridge Karnataka", page_icon="🌉", layout="wide")

# ---------- DB ----------
def get_conn():
    return psycopg2.connect(st.secrets["database"]["url"])

def run_query(sql, params=None, fetch=False):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    data = cur.fetchall() if fetch else None
    conn.commit()
    cur.close()
    conn.close()
    return data

def insert_many(sql, rows):
    conn = get_conn()
    cur = conn.cursor()
    execute_values(cur, sql, rows)
    conn.commit()
    cur.close()
    conn.close()

# ---------- Pages ----------
def page_student():
    st.title("🎓 Student Dashboard")
    user = st.session_state["user"]
    tabs = st.tabs(["🎯 Job Matching", "📝 My Applications", "🎓 Training", "🔔 Notifications"])

    with tabs[0]:
        jobs = run_query("SELECT id, title, company, district, sector, skills, qualification FROM jobs", fetch=True)
        if not jobs:
            st.info("No jobs yet.")
        else:
            df = pd.DataFrame(jobs, columns=["id","title","company","district","sector","skills","qualification"])
            for _, r in df.iterrows():
                with st.container(border=True):
                    st.subheader(r["title"])
                    st.write(f"**{r['company']}** • {r['district']} • {r['sector']}")
                    st.write(f"Skills: {r['skills']} | Qualification: {r['qualification']}")
                    if st.button("Apply", key=f"apply{r['id']}"):
                        run_query("INSERT INTO job_applications (student, job_id, status) VALUES (%s,%s,'Applied')", (user, r["id"]))
                        st.success("Application submitted!")

    with tabs[1]:
        apps = run_query("SELECT a.id, j.title, a.status, a.interview_date, a.feedback FROM job_applications a JOIN jobs j ON j.id=a.job_id WHERE a.student=%s", (user,), fetch=True)
        if apps:
            st.dataframe(pd.DataFrame(apps, columns=["ID","Job","Status","Interview","Feedback"]), use_container_width=True)
        else:
            st.info("No applications yet.")

    with tabs[2]:
        t = run_query("SELECT id, institute, program_name, skills_taught FROM training_programs", fetch=True)
        if t:
            df = pd.DataFrame(t, columns=["id","institute","program","skills"])
            st.dataframe(df, use_container_width=True)
            pid = st.number_input("Program ID to express interest", min_value=1, step=1)
            if st.button("I'm interested"):
                run_query("INSERT INTO training_interest (student, program_id) VALUES (%s,%s)", (user, int(pid)))
                st.success("Interest recorded!")
        else:
            st.info("No training programs yet.")

    with tabs[3]:
        n = run_query("SELECT message, created_at FROM notifications WHERE username=%s ORDER BY id DESC", (user,), fetch=True)
        if n:
            for m, d in n:
                st.info(f"{m} — {d}")
        else:
            st.info("No notifications.")

def page_company():
    st.title("🏢 Company Dashboard")
    user = st.session_state["user"]
    tab1, tab2, tab3 = st.tabs(["Post Job", "Applicants", "Interview & Feedback"])

    with tab1:
        with st.form("postjob"):
            title = st.text_input("Job title")
            desc = st.text_area("Description")
            skills = st.text_input("Required skills (comma separated)")
            qual = st.text_input("Qualification")
            district = st.text_input("District")
            sector = st.text_input("Sector")
            if st.form_submit_button("Post job"):
                run_query("INSERT INTO jobs (title, description, company, skills, qualification, district, sector) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                          (title, desc, user, skills, qual, district, sector))
                st.success("Job posted!")

    with tab2:
        apps = run_query("""SELECT a.id, a.student, j.title, a.status FROM job_applications a
                            JOIN jobs j ON j.id=a.job_id WHERE j.company=%s""", (user,), fetch=True)
        if apps:
            df = pd.DataFrame(apps, columns=["App ID","Student","Job","Status"])
            st.dataframe(df, use_container_width=True)
            aid = st.number_input("Application ID", min_value=1, step=1)
            new_status = st.selectbox("New status", ["Shortlisted","Interview","Selected","Rejected"])
            if st.button("Update status"):
                run_query("UPDATE job_applications SET status=%s WHERE id=%s", (new_status, int(aid)))
                run_query("INSERT INTO notifications (username, message) VALUES ((SELECT student FROM job_applications WHERE id=%s), %s)",
                          (int(aid), f"Your application status: {new_status}"))
                st.success("Status updated!")
        else:
            st.info("No applicants yet.")

    with tab3:
        st.write("Schedule interview / give feedback")
        aid = st.number_input("Application ID", min_value=1, step=1, key="fb")
        idate = st.date_input("Interview date", value=date.today())
        feedback = st.text_area("Feedback")
        if st.button("Save"):
            run_query("UPDATE job_applications SET interview_date=%s, feedback=%s WHERE id=%s", (idate, feedback, int(aid)))
            st.success("Saved!")

def page_institute():
    st.title("🎓 Training Institute")
    user = st.session_state["user"]
    with st.form("addprog"):
        name = st.text_input("Program name")
        skills = st.text_input("Skills taught (comma separated)")
        if st.form_submit_button("Add program"):
            run_query("INSERT INTO training_programs (institute, program_name, skills_taught) VALUES (%s,%s,%s)", (user, name, skills))
            st.success("Program added!")
    st.subheader("My programs")
    t = run_query("SELECT id, program_name, skills_taught FROM training_programs WHERE institute=%s", (user,), fetch=True)
    if t:
        st.dataframe(pd.DataFrame(t, columns=["ID","Program","Skills"]), use_container_width=True)

def page_admin():
    st.title("🏛️ District Dashboard")
    tab1, tab2, tab3 = st.tabs(["Analytics", "Job Matching", "Job Fair"])

    with tab1:
        students = run_query("SELECT COUNT(*) FROM students", fetch=True)[0][0]
        jobs = run_query("SELECT COUNT(*) FROM jobs", fetch=True)[0][0]
        apps = run_query("SELECT COUNT(*) FROM job_applications", fetch=True)[0][0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Students", students)
        c2.metric("Jobs", jobs)
        c3.metric("Applications", apps)

    with tab2:
        jobs = run_query("SELECT id, title, skills FROM jobs", fetch=True)
        if jobs:
            jid = st.selectbox("Choose job", jobs, format_func=lambda x: x[1])
            students = run_query("SELECT name, skills FROM students", fetch=True)
            req = set(s.strip().lower() for s in jid[2].split(",") if s.strip())
            for name, skills in students:
                have = set(s.strip().lower() for s in (skills or "").split(",") if s.strip())
                match = len(req & have)
                st.write(f"**{name}** — match {match}/{len(req)} skills | Missing: {', '.join(req-have) or 'None'}")
        else:
            st.info("No jobs.")

    with tab3:
        with st.form("fair"):
            fname = st.text_input("Fair name")
            fdate = st.date_input("Date", value=date.today())
            fdistrict = st.text_input("District")
            if st.form_submit_button("Create fair"):
                run_query("INSERT INTO job_fairs (name, date, district) VALUES (%s,%s,%s)", (fname, fdate, fdistrict))
                st.success("Fair created!")
        fairs = run_query("SELECT id, name, date, district FROM job_fairs", fetch=True)
        if fairs:
            st.dataframe(pd.DataFrame(fairs, columns=["ID","Name","Date","District"]), use_container_width=True)

def upload_csv():
    st.sidebar.subheader("📤 Bulk upload CSV")
    kind = st.sidebar.selectbox("Data type", ["Students","Jobs","Training programs"])
    file = st.sidebar.file_uploader("Upload CSV", type="csv")
    if file and st.sidebar.button("Upload"):
        df = pd.read_csv(file)
        if kind == "Students":
            rows = [(r["name"], r["district"], r["qualification"], r["skills"]) for _, r in df.iterrows()]
            insert_many("INSERT INTO students (name, district, qualification, skills) VALUES %s", rows)
        elif kind == "Jobs":
            rows = [(r["title"], r.get("description",""), r["company"], r["skills"], r["qualification"], r["district"], r["sector"]) for _, r in df.iterrows()]
            insert_many("INSERT INTO jobs (title, description, company, skills, qualification, district, sector) VALUES %s", rows)
        else:
            rows = [(r["institute"], r["program_name"], r["skills_taught"]) for _, r in df.iterrows()]
            insert_many("INSERT INTO training_programs (institute, program_name, skills_taught) VALUES %s", rows)
        st.sidebar.success(f"{len(df)} rows added!")

# ---------- Main ----------
def main():
    st.sidebar.title("🌉 Skill Bridge Karnataka")

    # One-click role switcher
    demo = {
        "Student (student1)": ("Student","student1","student123"),
        "Company (company1)": ("Company","company1","company123"),
        "Training Institute (institute1)": ("Training Institute","institute1","institute123"),
        "District Admin (admin)": ("District Admin","admin","admin123"),
        "State Admin (admin)": ("State Admin","admin","admin123"),
    }
    choice = st.sidebar.selectbox("🔄 Switch Role", list(demo.keys()))
    if st.sidebar.button("Switch now", use_container_width=True):
        role, user, pwd = demo[choice]
        st.session_state.update({"role": role, "user": user, "logged_in": True})
        st.rerun()

    if not st.session_state.get("logged_in"):
        st.title("Login")
        role = st.selectbox("Role", ["Student","Company","Training Institute","District Admin","State Admin"])
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            valid = {"student1":"student123","company1":"company123","institute1":"institute123","admin":"admin123"}
            if valid.get(user) == pwd:
                st.session_state.update({"role": role, "user": user, "logged_in": True})
                st.rerun()
            else:
                st.error("Wrong username or password")
        return

    st.sidebar.success(f"Logged in: {st.session_state['user']} ({st.session_state['role']})")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    upload_csv()

    role = st.session_state["role"]
    if role == "Student":
        page_student()
    elif role == "Company":
        page_company()
    elif role == "Training Institute":
        page_institute()
    else:
        page_admin()

main()
