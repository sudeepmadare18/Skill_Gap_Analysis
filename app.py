import streamlit as st
import pandas as pd
import psycopg2
import psycopg2.extras
import json
from pypdf import PdfReader
from docx import Document as DocxDocument

st.set_page_config(
    page_title="Skill Gap and Emerging Skills Intelligence",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Skill Gap and Emerging Skills Intelligence")
st.caption("Student CV, company jobs, skill-gap matching, job fair, and district dashboard.")

# ---------------- Database ----------------

def get_connection():
    return psycopg2.connect(
        st.secrets["DATABASE_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            degree TEXT,
            district TEXT,
            github TEXT,
            linkedin TEXT,
            skills TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            company TEXT,
            title TEXT,
            description TEXT,
            skills TEXT,
            degree TEXT,
            district TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_fairs (
            id SERIAL PRIMARY KEY,
            name TEXT,
            district TEXT,
            date TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fair_registrations (
            id SERIAL PRIMARY KEY,
            fair TEXT,
            student TEXT,
            skills TEXT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


init_db()

# ---------------- Skills ----------------

SKILL_DICT = {
    "Excel": ["excel"],
    "SQL": ["sql"],
    "Python": ["python"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Cloud computing": ["aws", "azure", "google cloud", "cloud computing", "cloud"],
    "Linux": ["linux"],
    "Machine learning": ["machine learning", "ml"],
    "Data analysis": ["data analysis", "data analytics"],
    "Communication": ["communication", "communication skills"],
    "Java": ["java"],
    "HTML": ["html"],
    "CSS": ["css"],
    "JavaScript": ["javascript", "js"],
    "React": ["react"],
    "Node.js": ["node.js", "nodejs"],
    "Git": ["git", "github"]
}

ALL_SKILLS = list(SKILL_DICT.keys())

TRAINING = {
    "Excel": "Advanced Excel and Data Reporting",
    "SQL": "SQL for Data Analysis",
    "Python": "Python Programming for Data and Automation",
    "Power BI": "Power BI Dashboard Development",
    "Tableau": "Tableau Data Visualisation",
    "Cloud computing": "Cloud Fundamentals and AWS Basics",
    "Linux": "Linux Administration Basics",
    "Machine learning": "Machine Learning Foundations",
    "Data analysis": "Data Analytics with Python",
    "Communication": "Professional Communication and Interview Skills",
    "Java": "Java Programming Fundamentals",
    "HTML": "Web Development with HTML",
    "CSS": "Web Development with CSS",
    "JavaScript": "JavaScript for Web Development",
    "React": "React Frontend Development",
    "Node.js": "Backend Development with Node.js",
    "Git": "Git and GitHub for Developers"
}

DISTRICTS = [
    "Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban",
    "Bidar", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru",
    "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad",
    "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar",
    "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara",
    "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura",
    "Yadgir"
]

ENGINEERING = [
    "Computer Science and Engineering",
    "Information Science and Engineering",
    "Artificial Intelligence and Machine Learning",
    "Data Science",
    "Electronics and Communication Engineering",
    "Electrical and Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Other Engineering Branch"
]

# ---------------- File reading ----------------

def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def read_docx(file):
    doc = DocxDocument(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def extract_skills(text):
    text = text.lower()
    found = []

    for skill, words in SKILL_DICT.items():
        for word in words:
            if word in text:
                found.append(skill)
                break

    return list(set(found))


def match_skills(student_skills, job_skills):
    student_set = set(student_skills)
    job_set = set(job_skills)

    matched = sorted(student_set & job_set)
    missing = sorted(job_set - student_set)

    score = 0 if not job_set else round(len(matched) / len(job_set) * 100, 1)

    return matched, missing, score

# ---------------- DB functions ----------------

def save_student(username, degree, district, github, linkedin, skills):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (username, degree, district, github, linkedin, skills)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (username)
        DO UPDATE SET
            degree = EXCLUDED.degree,
            district = EXCLUDED.district,
            github = EXCLUDED.github,
            linkedin = EXCLUDED.linkedin,
            skills = EXCLUDED.skills
    """, (username, degree, district, github, linkedin, json.dumps(skills)))

    conn.commit()
    cur.close()
    conn.close()


def get_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    students = []

    for row in rows:
        students.append({
            "Name": row["username"],
            "Degree": row["degree"],
            "District": row["district"],
            "GitHub": row["github"],
            "LinkedIn": row["linkedin"],
            "Skills": json.loads(row["skills"])
        })

    return students


def save_job(company, title, description, skills, degree, district):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO jobs (company, title, description, skills, degree, district)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (company, title, description, json.dumps(skills), degree, district))

    conn.commit()
    cur.close()
    conn.close()


def get_jobs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    jobs = []

    for row in rows:
        jobs.append({
            "Company": row["company"],
            "Title": row["title"],
            "Description": row["description"],
            "Skills": json.loads(row["skills"]),
            "Degree": row["degree"],
            "District": row["district"]
        })

    return jobs


def save_job_fair(name, district, date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO job_fairs (name, district, date)
        VALUES (%s, %s, %s)
    """, (name, district, date))

    conn.commit()
    cur.close()
    conn.close()


def get_job_fairs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM job_fairs ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "Name": row["name"],
            "District": row["district"],
            "Date": row["date"]
        }
        for row in rows
    ]


def delete_job_fair(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM job_fairs WHERE name = %s", (name,))

    conn.commit()
    cur.close()
    conn.close()


def save_registration(fair, student, skills):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO fair_registrations (fair, student, skills)
        VALUES (%s, %s, %s)
    """, (fair, student, skills))

    conn.commit()
    cur.close()
    conn.close()


def get_registrations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fair_registrations ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "Fair": row["fair"],
            "Student": row["student"],
            "Skills": row["skills"]
        }
        for row in rows
    ]


def delete_registration(fair, student):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM fair_registrations WHERE fair = %s AND student = %s",
        (fair, student)
    )

    conn.commit()
    cur.close()
    conn.close()


def clear_registrations():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM fair_registrations")

    conn.commit()
    cur.close()
    conn.close()

# ---------------- Session ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- Login ----------------

def login_page():
    st.title("🎯 Skill Gap and Emerging Skills Intelligence")
    st.subheader("Login")

    role = st.selectbox(
        "Select role",
        [
            "Student",
            "Company",
            "Training Institute",
            "District Admin",
            "State Admin",
            "Job Fair"
        ]
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Enter username and password.")

# ---------------- Student ----------------

def student_page():
    st.title("👤 Student Dashboard")

    saved_students = get_students()
    saved_profile = None

    for student in saved_students:
        if student["Name"] == st.session_state.username:
            saved_profile = student
            break

    if saved_profile:
        st.subheader("My saved profile")

        col1, col2, col3 = st.columns(3)

        col1.metric("Degree", saved_profile["Degree"])
        col2.metric("District", saved_profile["District"])
        col3.metric("Skills", len(saved_profile["Skills"]))

        st.write("**Saved skills:**")
        st.write(", ".join(saved_profile["Skills"]))

        st.divider()

    st.subheader("My profile")

    qualification = st.selectbox(
        "Qualification type",
        ["Engineering", "Degree", "PG", "Diploma", "ITI", "Other"]
    )

    if qualification == "Engineering":
        degree = st.selectbox("Engineering branch", ENGINEERING)
    else:
        degree = st.text_input("Enter degree / course name")

    district = st.selectbox("District", DISTRICTS)

    github = st.text_input("GitHub URL")
    linkedin = st.text_input("LinkedIn URL")

    cv = st.file_uploader("Upload CV", type=["pdf", "docx", "txt"])

    cv_text = ""

    if cv is not None:
        name = cv.name.lower()

        try:
            if name.endswith(".pdf"):
                cv_text = read_pdf(cv)
                st.success("PDF CV uploaded.")

            elif name.endswith(".docx"):
                cv_text = read_docx(cv)
                st.success("DOCX CV uploaded.")

            elif name.endswith(".txt"):
                cv_text = cv.read().decode("utf-8", errors="ignore")
                st.success("TXT CV uploaded.")

        except Exception:
            st.error("Could not read file.")

    manual_cv = st.text_area("Or paste CV / skills text")

    detected = extract_skills(cv_text + " " + manual_cv)

    skills = st.multiselect(
        "Confirm / add your skills",
        ALL_SKILLS,
        default=detected
    )

    if st.button("Save my profile"):
        if skills:
            save_student(
                st.session_state.username,
                degree,
                district,
                github,
                linkedin,
                skills
            )
            st.success("Profile saved permanently.")
        else:
            st.error("Select at least one skill.")

    st.subheader("My skills")
    st.write(", ".join(skills) if skills else "None")

# ---------------- Company ----------------

def company_page():
    st.title("🏢 Company Dashboard")

    st.subheader("Post a job")

    job_title = st.text_input("Job title")
    job_description = st.text_area("Job description")

    detected = extract_skills(job_description)

    job_skills = st.multiselect(
        "Required job skills",
        ALL_SKILLS,
        default=detected
    )

    degree = st.selectbox(
        "Required qualification",
        [
            "Any qualification", "Engineering", "BCA", "B.Sc.", "B.Com",
            "BA", "MCA", "M.Sc.", "MBA", "Diploma", "ITI"
        ]
    )

    district = st.selectbox("Job district", DISTRICTS)

    if st.button("Save job"):
        if job_title and job_skills:
            save_job(
                st.session_state.username,
                job_title,
                job_description,
                job_skills,
                degree,
                district
            )
            st.success("Job saved permanently.")
        else:
            st.error("Enter job title and select skills.")

    st.subheader("All jobs")

    jobs = get_jobs()

    if jobs:
        rows = []

        for job in jobs:
            rows.append({
                "Company": job["Company"],
                "Job": job["Title"],
                "District": job["District"],
                "Skills": ", ".join(job["Skills"])
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No jobs posted yet.")

# ---------------- Matching ----------------

def matching_page():
    st.title("🎯 Job Matching and Skill Gap")

    jobs = get_jobs()
    students = get_students()

    if not jobs:
        st.warning("No jobs posted.")
        st.stop()

    if not students:
        st.warning("No students added.")
        st.stop()

    job_options = [
        f"{job['Title']} — {job['Company']} ({job['District']})"
        for job in jobs
    ]

    selected_job = st.selectbox("Choose job", job_options)

    job = jobs[job_options.index(selected_job)]

    st.write("**Required skills:**")
    st.write(", ".join(job["Skills"]))

    results = []

    for student in students:
        matched, missing, score = match_skills(
            student["Skills"],
            job["Skills"]
        )

        results.append({
            "Student": student["Name"],
            "Degree": student["Degree"],
            "District": student["District"],
            "Match score": score,
            "Matched skills": ", ".join(matched) if matched else "None",
            "Missing skills": ", ".join(missing) if missing else "None"
        })

    df = pd.DataFrame(results).sort_values("Match score", ascending=False)

    st.subheader("Student ranking")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download matching report",
        csv,
        "student_job_matching.csv",
        "text/csv"
    )

    st.subheader("Detailed skill-gap report")

    student_names = [student["Name"] for student in students]

    selected_student = st.selectbox("Choose student", student_names)

    student = next(
        s for s in students
        if s["Name"] == selected_student
    )

    matched, missing, score = match_skills(
        student["Skills"],
        job["Skills"]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Match score", f"{score}%")
    col2.metric("Matched skills", len(matched))
    col3.metric("Missing skills", len(missing))

    st.subheader("Matched skills")
    st.write(", ".join(matched) if matched else "None")

    st.subheader("Missing skills / Skill gap")
    st.write(", ".join(missing) if missing else "No skill gap.")

    st.subheader("Recommended training")

    if missing:
        rows = []

        for skill in missing:
            rows.append({
                "Missing skill": skill,
                "Recommended training": TRAINING.get(
                    skill,
                    "Skill-specific training"
                )
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ---------------- Job fair ----------------

def job_fair_page():
    st.title("🎪 Job Fair")

    tab1, tab2, tab3 = st.tabs([
        "Create job fair",
        "Student registration",
        "Participants"
    ])

    with tab1:
        fair_name = st.text_input("Job fair name")
        fair_district = st.selectbox("District", DISTRICTS)
        fair_date = st.date_input("Job fair date")

        if st.button("Create job fair"):
            if fair_name:
                save_job_fair(
                    fair_name,
                    fair_district,
                    str(fair_date)
                )
                st.success("Job fair saved permanently.")
            else:
                st.error("Enter fair name.")

        st.subheader("Job fairs")

        fairs = get_job_fairs()

        if fairs:
            for fair in fairs:
                col1, col2, col3 = st.columns([3, 2, 1])

                col1.write(f"**{fair['Name']}**")
                col2.write(f"{fair['District']} — {fair['Date']}")

                if col3.button("Delete", key=f"delete_fair_{fair['Name']}"):
                    delete_job_fair(fair["Name"])
                    st.rerun()
        else:
            st.info("No job fairs yet.")

    with tab2:
        fairs = get_job_fairs()

        if not fairs:
            st.warning("No job fairs available.")
            st.stop()

        fair_options = [
            f"{fair['Name']} — {fair['District']} ({fair['Date']})"
            for fair in fairs
        ]

        selected_fair = st.selectbox("Choose job fair", fair_options)

        student_name = st.text_input("Student name")

        if st.button("Register"):
            if student_name:
                skills = "No skills added"

                for student in get_students():
                    if student["Name"] == student_name:
                        skills = ", ".join(student["Skills"])
                        break

                save_registration(
                    selected_fair,
                    student_name,
                    skills
                )

                st.success("Student registered permanently.")
            else:
                st.error("Enter student name.")

    with tab3:
        st.subheader("Registered students")

        registrations = get_registrations()

        if registrations:
            for registration in registrations:
                col1, col2, col3 = st.columns([3, 3, 1])

                col1.write(f"**{registration['Student']}**")
                col2.write(registration["Skills"])

                if col3.button(
                    "Delete",
                    key=f"delete_reg_{registration['Fair']}_{registration['Student']}"
                ):
                    delete_registration(
                        registration["Fair"],
                        registration["Student"]
                    )
                    st.rerun()

            st.subheader("Registration table")
            st.dataframe(
                pd.DataFrame(registrations),
                use_container_width=True
            )

            if st.button("Clear all registrations"):
                clear_registrations()
                st.rerun()

        else:
            st.info("No registrations yet.")

# ---------------- Dashboard ----------------

def admin_page():
    st.title("🏛️ District and State Skill Dashboard")

    students = get_students()
    jobs = get_jobs()
    fairs = get_job_fairs()
    registrations = get_registrations()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total students", len(students))
    col2.metric("Total jobs", len(jobs))
    col3.metric("Job fairs", len(fairs))
    col4.metric("Fair registrations", len(registrations))

    st.divider()

    all_districts = sorted(
        list(set(
            [student["District"] for student in students] +
            [job["District"] for job in jobs]
        ))
    )

    selected_district = st.selectbox(
        "Select district",
        ["All Karnataka"] + all_districts
    )

    if selected_district == "All Karnataka":
        filtered_students = students
        filtered_jobs = jobs
    else:
        filtered_students = [
            student for student in students
            if student["District"] == selected_district
        ]

        filtered_jobs = [
            job for job in jobs
            if job["District"] == selected_district
        ]

    st.subheader(f"Selected area: {selected_district}")

    col1, col2 = st.columns(2)

    col1.metric("Students", len(filtered_students))
    col2.metric("Jobs", len(filtered_jobs))

    st.divider()

    st.subheader("Top skills demanded by companies")

    skill_count = {}

    for job in filtered_jobs:
        for skill in job["Skills"]:
            skill_count[skill] = skill_count.get(skill, 0) + 1

    if skill_count:
        skill_df = pd.DataFrame(
            sorted(skill_count.items(), key=lambda x: x[1], reverse=True),
            columns=["Skill", "Number of jobs"]
        )

        st.bar_chart(skill_df.set_index("Skill"))
        st.dataframe(skill_df, use_container_width=True)
    else:
        st.info("No job skills available.")

    st.divider()

    st.subheader("Skills available among students")

    student_skill_count = {}

    for student in filtered_students:
        for skill in student["Skills"]:
            student_skill_count[skill] = student_skill_count.get(skill, 0) + 1

    if student_skill_count:
        student_skill_df = pd.DataFrame(
            sorted(student_skill_count.items(), key=lambda x: x[1], reverse=True),
            columns=["Skill", "Number of students"]
        )

        st.bar_chart(student_skill_df.set_index("Skill"))
        st.dataframe(student_skill_df, use_container_width=True)
    else:
        st.info("No student skills available.")

    st.divider()

    st.subheader("District-wise students")

    if students:
        district_students = {}

        for student in students:
            district_students[student["District"]] = district_students.get(
                student["District"], 0
            ) + 1

        district_df = pd.DataFrame(
            sorted(district_students.items(), key=lambda x: x[1], reverse=True),
            columns=["District", "Students"]
        )

        st.bar_chart(district_df.set_index("District"))
        st.dataframe(district_df, use_container_width=True)

    st.divider()

    st.subheader("District-wise jobs")

    if jobs:
        district_jobs = {}

        for job in jobs:
            district_jobs[job["District"]] = district_jobs.get(
                job["District"], 0
            ) + 1

        job_district_df = pd.DataFrame(
            sorted(district_jobs.items(), key=lambda x: x[1], reverse=True),
            columns=["District", "Jobs"]
        )

        st.bar_chart(job_district_df.set_index("District"))
        st.dataframe(job_district_df, use_container_width=True)

    st.divider()

    st.subheader("Skill gap summary")

    if filtered_jobs and filtered_students:
        job_skills = set()
        student_skills = set()

        for job in filtered_jobs:
            job_skills.update(job["Skills"])

        for student in filtered_students:
            student_skills.update(student["Skills"])

        missing_skills = sorted(job_skills - student_skills)

        if missing_skills:
            st.warning("Skills required by jobs but not available among students:")

            gap_rows = []

            for skill in missing_skills:
                gap_rows.append({
                    "Missing skill": skill,
                    "Recommended training": TRAINING.get(
                        skill,
                        "Skill-specific training"
                    )
                })

            gap_df = pd.DataFrame(gap_rows)

            st.dataframe(gap_df, use_container_width=True)

            csv = gap_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download skill-gap report",
                csv,
                "skill_gap_report.csv",
                "text/csv"
            )

        else:
            st.success("No major skill gap found for the selected area.")
    else:
        st.info("Add students and jobs to see skill gap.")

    st.divider()

    st.subheader("Job fair participants")

    if registrations:
        participants_df = pd.DataFrame(registrations)

        st.dataframe(participants_df, use_container_width=True)

        csv = participants_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download job-fair participants",
            csv,
            "job_fair_participants.csv",
            "text/csv"
        )
    else:
        st.info("No job-fair registrations yet.")

# ---------------- Main ----------------

def main():
    if not st.session_state.logged_in:
        login_page()
        return

    st.sidebar.title("Navigation")
    st.sidebar.write(f"**Role:** {st.session_state.role}")
    st.sidebar.write(f"**User:** {st.session_state.username}")

    page = st.sidebar.radio(
        "Go to",
        [
            "Home",
            "🎯 Job Matching",
            "🎪 Job Fair",
            "🏛️ District Dashboard"
        ]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = ""
        st.rerun()

    if page == "🎯 Job Matching":
        matching_page()

    elif page == "🎪 Job Fair":
        job_fair_page()

    elif page == "🏛️ District Dashboard":
        admin_page()

    elif st.session_state.role == "Student":
        student_page()

    elif st.session_state.role == "Company":
        company_page()

    else:
        admin_page()

main()
