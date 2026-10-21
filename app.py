import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Skill Gap and Emerging Skills Intelligence",
    page_icon="🎯",
    layout="wide"
)

# ---------------- Initialise session ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "student_skills" not in st.session_state:
    st.session_state.student_skills = []

if "job_skills" not in st.session_state:
    st.session_state.job_skills = []

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

# ---------------- Helper functions ----------------

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
    extra = sorted(student_set - job_set)

    match_score = 0 if not job_set else round(len(matched) / len(job_set) * 100, 1)

    return matched, missing, extra, match_score

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

    tab1, tab2 = st.tabs(["👤 My CV and Skills", "🎯 Job Matching"])

    with tab1:
        st.subheader("My profile")

        degree = st.selectbox(
            "Degree",
            ["BCA", "B.Sc.", "B.Com", "BA", "MCA", "M.Sc.", "MBA", "Other"]
        )

        district = st.selectbox(
            "District",
            [
                "Bengaluru Urban",
                "Mysuru",
                "Belagavi",
                "Kalaburagi",
                "Dharwad",
                "Dakshina Kannada",
                "Other"
            ]
        )

        github_url = st.text_input("GitHub profile URL")
        linkedin_url = st.text_input("LinkedIn profile URL")

        cv_file = st.file_uploader("Upload CV (TXT)", type=["txt"])
        cv_text = ""

        if cv_file is not None:
            cv_text = cv_file.read().decode("utf-8", errors="ignore")
            st.success("CV uploaded.")

        manual_cv = st.text_area("Or paste CV / skills text")

        detected = extract_skills(cv_text + " " + manual_cv)

        st.session_state.student_skills = st.multiselect(
            "Confirm / add your skills",
            ALL_SKILLS,
            default=st.session_state.student_skills or detected
        )

        st.success(
            "Saved skills: "
            + (", ".join(st.session_state.student_skills) if st.session_state.student_skills else "None")
        )

    with tab2:
        st.subheader("Match your skills with a job")

        if not st.session_state.job_skills:
            st.info("No job has been posted yet. Please ask a company to post a job.")
            st.stop()

        matched, missing, extra, score = calculate_match(
            st.session_state.student_skills,
            st.session_state.job_skills
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("JD-to-CV match score", f"{score}%")
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

# ---------------- Company dashboard ----------------

def company_dashboard():
    st.title(f"🏢 Company Dashboard — {st.session_state.username}")

    st.subheader("Post a job")

    job_title = st.text_input("Job title")
    job_description = st.text_area("Job description / responsibilities")

    detected = extract_skills(job_description)

    st.session_state.job_skills = st.multiselect(
        "Required job skills",
        ALL_SKILLS,
        default=st.session_state.job_skills or detected
    )

    required_degree = st.selectbox(
        "Required degree",
        ["Any degree", "BCA", "B.Sc.", "B.Com", "BA", "MCA", "M.Sc.", "MBA"]
    )

    job_district = st.selectbox(
        "Job district",
        [
            "Bengaluru Urban",
            "Mysuru",
            "Belagavi",
            "Kalaburagi",
            "Dharwad",
            "Dakshina Kannada",
            "Other"
        ]
    )

    if st.button("Save job posting"):
        if job_title and st.session_state.job_skills:
            st.success("Job posted successfully.")
        else:
            st.error("Enter job title and select at least one required skill.")

    st.subheader("Current job requirements")
    st.write(", ".join(st.session_state.job_skills) if st.session_state.job_skills else "None")

# ---------------- Admin dashboard ----------------

def admin_dashboard():
    st.title("🏛️ Labour and Skill Department Dashboard")

    st.info(
        "This dashboard will show district-wise and state-wise job openings, "
        "skill demand, student employment data, and sector growth."
    )

    st.subheader("Current platform data")

    col1, col2 = st.columns(2)

    col1.metric("Student skills entered", len(st.session_state.student_skills))
    col2.metric("Job skills required", len(st.session_state.job_skills))

    st.subheader("Skill demand and supply snapshot")

    data = pd.DataFrame({
        "Category": ["Student skills", "Job-required skills"],
        "Count": [
            len(st.session_state.student_skills),
            len(st.session_state.job_skills)
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

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = ""
        st.rerun()

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
