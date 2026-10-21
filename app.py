import streamlit as st
import pandas as pd
from pypdf import PdfReader
from docx import Document as DocxDocument

st.set_page_config(
    page_title="Skill Gap and Emerging Skills Intelligence",
    page_icon="🎯",
    layout="wide"
)

# ---------------- Session state ----------------

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

# ---------------- Skill dictionary ----------------

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

TRAINING_RECOMMENDATIONS = {
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

KARNATAKA_DISTRICTS = [
    "Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban",
    "Bidar", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru",
    "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad",
    "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar",
    "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara",
    "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura",
    "Yadgir"
]

ENGINEERING_BRANCHES = [
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

# ---------------- Helper functions ----------------

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def extract_text_from_docx(file):
    document = DocxDocument(file)
    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_skills(text):
    text = text.lower()
    found = []

    for skill, keywords in SKILL_DICT.items():
        for keyword in keywords:
            if keyword in text:
                found.append(skill)
                break

    return list(set(found))


def calculate_match(student_skills, job_skills):
    student_set = set(student_skills)
    job_set = set(job_skills)

    matched = sorted(student_set & job_set)
    missing = sorted(job_set - student_set)

    score = 0 if not job_set else round(len(matched) / len(job_set) * 100, 1)

    return matched, missing, score

# ---------------- Login page ----------------

def login_page():
    st.title("🎯 Skill Gap and Emerging Skills Intelligence")
    st.subheader("Login")

    role = st.selectbox(
        "Select your role",
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
            st.error("Please enter username and password.")

# ---------------- Student dashboard ----------------

def student_dashboard():
    st.title(f"👤 Student Dashboard — {st.session_state.username}")

    st.subheader("Add / update your profile")

    qualification_type = st.selectbox(
        "Qualification type",
        ["Engineering", "Degree", "PG", "Diploma", "ITI", "Other"]
    )

    if qualification_type == "Engineering":
        degree = st.selectbox("Engineering branch", ENGINEERING_BRANCHES)
    else:
        degree = st.text_input("Enter degree / course name")

    district = st.selectbox("District", KARNATAKA_DISTRICTS)

    github_url = st.text_input("GitHub profile URL")
    linkedin_url = st.text_input("LinkedIn profile URL")

    cv_file = st.file_uploader(
        "Upload CV",
        type=["pdf", "docx", "txt"]
    )

    cv_text = ""

    if cv_file is not None:
        file_name = cv_file.name.lower()

        try:
            if file_name.endswith(".pdf"):
                cv_text = extract_text_from_pdf(cv_file)
                st.success("PDF CV uploaded and text extracted.")

            elif file_name.endswith(".docx"):
                cv_text = extract_text_from_docx(cv_file)
                st.success("DOCX CV uploaded and text extracted.")

            elif file_name.endswith(".txt"):
                cv_text = cv_file.read().decode("utf-8", errors="ignore")
                st.success("TXT CV uploaded and text extracted.")

        except Exception:
            st.error("Could not read this file. Please try another CV file.")

    manual_cv = st.text_area("Or paste your CV / skills text")

    detected_skills = extract_skills(cv_text + " " + manual_cv)

    selected_skills = st.multiselect(
        "Confirm / add your skills",
        ALL_SKILLS,
        default=detected_skills
    )

    if st.button("Save my profile"):
        if st.session_state.username and selected_skills:
            for student in st.session_state.students:
                if student["Name"] == st.session_state.username:
                    student["Skills"] = selected_skills
                    student["Degree"] = degree
                    student["District"] = district
                    break
            else:
                st.session_state.students.append({
                    "Name": st.session_state.username,
                    "Degree": degree,
                    "District": district,
                    "GitHub": github_url,
                    "LinkedIn": linkedin_url,
                    "Skills": selected_skills
                })

            st.success("Profile saved successfully.")
        else:
            st.error("Select at least one skill.")

    st.subheader("My saved skills")
    st.write(", ".join(selected_skills) if selected_skills else "None")

# ---------------- Company dashboard ----------------

def company_dashboard():
    st.title(f"🏢 Company Dashboard — {st.session_state.username}")

    st.subheader("Post a job")

    job_title = st.text_input("Job title")
    job_description = st.text_area("Job description / responsibilities")

    detected_job_skills = extract_skills(job_description)

    selected_job_skills = st.multiselect(
        "Required job skills",
        ALL_SKILLS,
        default=detected_job_skills
    )

    required_degree = st.selectbox(
        "Required qualification",
        [
            "Any qualification",
            "Engineering",
            "BCA",
            "B.Sc.",
            "B.Com",
            "BA",
            "MCA",
            "M.Sc.",
            "MBA",
            "Diploma",
            "ITI"
        ]
    )

    job_district = st.selectbox(
        "Job district",
        KARNATAKA_DISTRICTS
    )

    if st.button("Save job posting"):
        if job_title and selected_job_skills:
            st.session_state.jobs.append({
                "Company": st.session_state.username,
                "Title": job_title,
                "Description": job_description,
                "Skills": selected_job_skills,
                "Degree": required_degree,
                "District": job_district
            })

            st.success("Job posted successfully.")
        else:
            st.error("Enter job title and select at least one required skill.")

    st.subheader(f"My posted jobs: {len(st.session_state.jobs)}")

    if st.session_state.jobs:
        job_rows = []

        for job in st.session_state.jobs:
            job_rows.append({
                "Job title": job["Title"],
                "District": job["District"],
                "Required skills": ", ".join(job["Skills"])
            })

        st.dataframe(pd.DataFrame(job_rows), use_container_width=True)

# ---------------- Matching dashboard ----------------

def matching_dashboard():
    st.title("🎯 Job Matching and Skill Gap")

    if not st.session_state.jobs:
        st.warning("No jobs posted yet.")
        st.stop()

    if not st.session_state.students:
        st.warning("No students added yet.")
        st.stop()

    job_options = [
        f"{job['Title']} — {job['Company']} ({job['District']})"
        for job in st.session_state.jobs
    ]

    selected_job = st.selectbox("Choose job", job_options)

    job_index = job_options.index(selected_job)
    job = st.session_state.jobs[job_index]

    st.write("**Required skills:**")
    st.write(", ".join(job["Skills"]))

    results = []

    for student in st.session_state.students:
        matched, missing, score = calculate_match(
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

    result_df = pd.DataFrame(results).sort_values(
        "Match score",
        ascending=False
    )

    st.subheader("Student ranking for this job")
    st.dataframe(result_df, use_container_width=True)

    st.subheader("Detailed skill-gap report")

    student_options = [
        student["Name"] for student in st.session_state.students
    ]

    selected_student_name = st.selectbox(
        "Choose student",
        student_options
    )

    selected_student = next(
        student for student in st.session_state.students
        if student["Name"] == selected_student_name
    )

    matched, missing, score = calculate_match(
        selected_student["Skills"],
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
                "Recommended training": TRAINING_RECOMMENDATIONS.get(
                    skill,
                    "Skill-specific training programme"
                )
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.success("No training required based on listed job skills.")

# ---------------- Admin dashboard ----------------

def admin_dashboard():
    st.title("🏛️ Labour and Skill Department Dashboard")

    st.info(
        "This dashboard will show district-wise and state-wise job openings, "
        "skill demand, student employment data, and sector growth."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Students added", len(st.session_state.students))
    col2.metric("Jobs posted", len(st.session_state.jobs))
    col3.metric(
        "Total student skills",
        sum(len(student["Skills"]) for student in st.session_state.students)
    )

    st.subheader("Platform snapshot")

    data = pd.DataFrame({
        "Category": ["Students", "Jobs"],
        "Count": [
            len(st.session_state.students),
            len(st.session_state.jobs)
        ]
    })

    st.bar_chart(data.set_index("Category"))

# ---------------- Main app ----------------

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
            "🎯 Job Matching and Skill Gap"
        ]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = ""
        st.rerun()

    if page == "🎯 Job Matching and Skill Gap":
        matching_dashboard()
        return

    if st.session_state.role == "Student":
        student_dashboard()

    elif st.session_state.role == "Company":
        company_dashboard()

    elif st.session_state.role in [
        "Training Institute",
        "District Admin",
        "State Admin",
        "Job Fair"
    ]:
        admin_dashboard()

main()
