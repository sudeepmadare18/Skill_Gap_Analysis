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
    extra = sorted(student_set - job_set)

    match_score = 0 if not job_set else round(len(matched) / len(job_set) * 100, 1)

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

    qualification_type = st.selectbox(
        "Qualification type",
        [
            "Engineering",
            "Degree",
            "PG",
            "Diploma",
            "ITI",
            "Other"
        ]
    )

    if qualification_type == "Engineering":
        student_degree = st.selectbox(
            "Engineering branch",
            ENGINEERING_BRANCHES
        )
    else:
        student_degree = st.text_input("Enter degree / course name")

    district = st.selectbox(
        "District",
        KARNATAKA_DISTRICTS
    )

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

        except Exception as e:
            st.error("Could not read this file. Please try another CV file.")

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

        st.dataframe(pd.DataFrame(recommendations), use_container_width=True)

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
