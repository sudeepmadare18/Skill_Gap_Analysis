import streamlit as st
import pandas as pd
from pypdf import PdfReader
from docx import Document as DocxDocument

st.set_page_config(
    page_title="Skill Gap and Emerging Skills Intelligence",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Skill Gap and Emerging Skills Intelligence")
st.caption("Student CV, company jobs, skill-gap matching, and job fair module.")

# ---------------- Session storage ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "students" not in st.session_state:
    st.session_state.students = []

if "jobs" not in st.session_state:
    st.session_state.jobs = []

if "job_fairs" not in st.session_state:
    st.session_state.job_fairs = []

if "fair_registrations" not in st.session_state:
    st.session_state.fair_registrations = []

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

# ---------------- Functions ----------------

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
            for student in st.session_state.students:
                if student["Name"] == st.session_state.username:
                    student["Skills"] = skills
                    student["Degree"] = degree
                    student["District"] = district
                    break
            else:
                st.session_state.students.append({
                    "Name": st.session_state.username,
                    "Degree": degree,
                    "District": district,
                    "GitHub": github,
                    "LinkedIn": linkedin,
                    "Skills": skills
                })

            st.success("Profile saved.")
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
            st.session_state.jobs.append({
                "Company": st.session_state.username,
                "Title": job_title,
                "Description": job_description,
                "Skills": job_skills,
                "Degree": degree,
                "District": district
            })
            st.success("Job posted.")
        else:
            st.error("Enter job title and select skills.")

    st.subheader(f"My jobs: {len(st.session_state.jobs)}")

    if st.session_state.jobs:
        rows = []

        for job in st.session_state.jobs:
            rows.append({
                "Job": job["Title"],
                "District": job["District"],
                "Skills": ", ".join(job["Skills"])
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ---------------- Matching ----------------

def matching_page():
    st.title("🎯 Job Matching and Skill Gap")

    if not st.session_state.jobs:
        st.warning("No jobs posted.")
        st.stop()

    if not st.session_state.students:
        st.warning("No students added.")
        st.stop()

    job_options = [
        f"{job['Title']} — {job['Company']} ({job['District']})"
        for job in st.session_state.jobs
    ]

    selected_job = st.selectbox("Choose job", job_options)

    job = st.session_state.jobs[job_options.index(selected_job)]

    st.write("**Required skills:**")
    st.write(", ".join(job["Skills"]))

    results = []

    for student in st.session_state.students:
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

    st.subheader("Detailed skill-gap report")

    student_names = [student["Name"] for student in st.session_state.students]

    selected_student = st.selectbox("Choose student", student_names)

    student = next(
        s for s in st.session_state.students
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
                st.session_state.job_fairs.append({
                    "Name": fair_name,
                    "District": fair_district,
                    "Date": str(fair_date)
                })
                st.success("Job fair created.")
            else:
                st.error("Enter fair name.")

        st.subheader(f"Job fairs: {len(st.session_state.job_fairs)}")

        if st.session_state.job_fairs:
            rows = []

            for fair in st.session_state.job_fairs:
                rows.append({
                    "Fair": fair["Name"],
                    "District": fair["District"],
                    "Date": fair["Date"]
                })

            st.dataframe(pd.DataFrame(rows), use_container_width=True)

    with tab2:
        if not st.session_state.job_fairs:
            st.warning("No job fairs available.")
            st.stop()

        fair_options = [
            f"{fair['Name']} — {fair['District']} ({fair['Date']})"
            for fair in st.session_state.job_fairs
        ]

        selected_fair = st.selectbox("Choose job fair", fair_options)

        student_name = st.text_input("Student name")

        if st.button("Register"):
            if student_name:
                skills = "No skills added"

                for student in st.session_state.students:
                    if student["Name"] == student_name:
                        skills = ", ".join(student["Skills"])
                        break

                st.session_state.fair_registrations.append({
                    "Fair": selected_fair,
                    "Student": student_name,
                    "Skills": skills
                })

                st.success("Student registered.")
            else:
                st.error("Enter student name.")

    with tab3:
        st.subheader("Registered students")

        if st.session_state.fair_registrations:
            st.dataframe(
                pd.DataFrame(st.session_state.fair_registrations),
                use_container_width=True
            )
        else:
            st.info("No registrations yet.")

# ---------------- Admin ----------------

def admin_page():
    st.title("🏛️ Labour and Skill Department Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Students", len(st.session_state.students))
    col2.metric("Jobs", len(st.session_state.jobs))
    col3.metric("Job fairs", len(st.session_state.job_fairs))

    st.subheader("Platform snapshot")

    data = pd.DataFrame({
        "Category": ["Students", "Jobs", "Job fairs"],
        "Count": [
            len(st.session_state.students),
            len(st.session_state.jobs),
            len(st.session_state.job_fairs)
        ]
    })

    st.bar_chart(data.set_index("Category"))

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
            "🎪 Job Fair"
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

    elif st.session_state.role == "Student":
        student_page()

    elif st.session_state.role == "Company":
        company_page()

    else:
        admin_page()

main()
