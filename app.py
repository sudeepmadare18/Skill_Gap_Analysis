import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(
    page_title="Skill Gap and Emerging Skills Intelligence",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Skill Gap and Emerging Skills Intelligence")
st.caption(
    "Module 1: Student CV vs Job Description skill-gap analysis, "
    "job matching, and training recommendation."
)

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
    "Git": ["git", "github"],
}

ALL_SKILLS = list(SKILL_DICT.keys())

# ---------------- Training recommendations ----------------

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

    if len(job_set) == 0:
        match_score = 0
    else:
        match_score = round(len(matched) / len(job_set) * 100, 1)

    return matched, missing, extra, match_score

# ---------------- Main layout ----------------

tab1, tab2, tab3 = st.tabs([
    "👤 Student CV",
    "🏢 Job Description",
    "🎯 Skill Gap and Matching"
])

# ---------------- Student CV tab ----------------

with tab1:
    st.subheader("Student profile and CV")

    student_name = st.text_input("Student name")
    student_degree = st.selectbox(
        "Degree",
        [
            "BCA",
            "B.Sc.",
            "B.Com",
            "BA",
            "MCA",
            "M.Sc.",
            "MBA",
            "Other"
        ]
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

    cv_file = st.file_uploader(
        "Upload CV (TXT file for this prototype)",
        type=["txt"]
    )

    cv_text = ""

    if cv_file is not None:
        cv_text = cv_file.read().decode("utf-8", errors="ignore")
        st.success("CV uploaded successfully.")

    manual_cv = st.text_area(
        "Or paste your CV / skills text",
        value=""
    )

    final_cv_text = cv_text + " " + manual_cv

    detected_student_skills = extract_skills(final_cv_text)

    selected_student_skills = st.multiselect(
        "Confirm / add your skills",
        ALL_SKILLS,
        default=detected_student_skills
    )

    st.success(
        "Student skills saved: "
        + (", ".join(selected_student_skills) if selected_student_skills else "None")
    )

# ---------------- Job description tab ----------------

with tab2:
    st.subheader("Company job posting")

    company_name = st.text_input("Company name")
    job_title = st.text_input("Job title")

    job_description = st.text_area(
        "Paste job description / responsibilities",
        value=""
    )

    selected_job_skills = st.multiselect(
        "Confirm / add required job skills",
        ALL_SKILLS,
        default=extract_skills(job_description)
    )

    required_degree = st.selectbox(
        "Required degree",
        [
            "Any degree",
            "BCA",
            "B.Sc.",
            "B.Com",
            "BA",
            "MCA",
            "M.Sc.",
            "MBA"
        ]
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

    st.success(
        "Job requirements saved: "
        + (", ".join(selected_job_skills) if selected_job_skills else "None")
    )

# ---------------- Skill gap tab ----------------

with tab3:
    st.subheader("Student CV vs Job Description")

    if not selected_student_skills:
        st.warning("Please select at least one student skill in the Student CV tab.")
        st.stop()

    if not selected_job_skills:
        st.warning("Please select at least one required job skill in the Job Description tab.")
        st.stop()

    matched, missing, extra, match_score = calculate_match(
        selected_student_skills,
        selected_job_skills
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("JD-to-CV match score", f"{match_score}%")
    col2.metric("Matched skills", len(matched))
    col3.metric("Missing skills", len(missing))

    st.subheader("Matched skills")
    st.write(", ".join(matched) if matched else "None")

    st.subheader("Missing skills / Skill gap")
    st.write(", ".join(missing) if missing else "No skill gap. Student meets all listed job skills.")

    st.subheader("Additional student skills")
    st.write(", ".join(extra) if extra else "None")

    st.subheader("Skill-gap visualisation")

    gap_data = pd.DataFrame({
        "Category": ["Matched skills", "Missing skills"],
        "Count": [len(matched), len(missing)]
    })

    st.bar_chart(gap_data.set_index("Category"))

    st.subheader("Recommended training to fill the gap")

    if missing:
        recommendations = []

        for skill in missing:
            recommendations.append({
                "Missing skill": skill,
                "Recommended training": TRAINING_RECOMMENDATIONS.get(
                    skill,
                    "Skill-specific training programme"
                )
            })

        recommendation_df = pd.DataFrame(recommendations)
        st.dataframe(recommendation_df, use_container_width=True)

    else:
        st.success("No training recommendation required based on the listed job skills.")

    st.subheader("Student roadmap")

    if missing:
        roadmap = []

        for i, skill in enumerate(missing, start=1):
            roadmap.append(
                f"{i}. Learn {skill} through: "
                f"{TRAINING_RECOMMENDATIONS.get(skill, 'Skill-specific training programme')}"
            )

        st.write("\n".join(roadmap))
    else:
        st.write("Student already covers the listed job requirements. Focus on interview preparation and portfolio building.")

    st.info(
        "This match is based on skills listed in the student CV and job description. "
        "It does not verify real proficiency. GitHub, LinkedIn, projects, certifications, "
        "and assessments can be used later for deeper skill verification."
    )
