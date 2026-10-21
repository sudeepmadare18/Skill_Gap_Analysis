# 🎯 Skill Gap and Emerging Skills Intelligence

A Streamlit-based prototype that helps match students with company job requirements, identify skill gaps, recommend training, and manage job-fair registrations.

## 📌 Problem Statement

Students often do not know which skills are required for jobs, and companies find it difficult to identify suitable candidates. This application extracts skills from student CVs, compares them with job requirements, calculates a skill-gap score, and recommends relevant training.

## 🚀 Features

- Student login and profile creation
- CV upload in PDF, DOCX, and TXT format
- Automatic skill extraction from CV text
- Company job posting with required skills
- Student-vs-job skill matching
- Match score, matched skills, and missing skills
- Training recommendations for skill gaps
- Multiple students and multiple jobs with ranking
- Job-fair creation and student registration
- Delete job fairs and registrations
- District and state dashboard
- Skill-demand and student-skill charts
- District-wise student and job analysis
- Skill-gap summary and training recommendations
- CSV download for matching, skill-gap, and job-fair participant reports
- Permanent data storage using PostgreSQL (Neon)

## 👥 User Roles

- Student
- Company
- Training Institute
- District Admin
- State Admin
- Job Fair

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- PostgreSQL
- Neon Cloud Database
- psycopg2
- pypdf
- python-docx

## 🗂️ Modules

| Module | Description |
|---|---|
| Student CV Analysis | Upload CV, extract and confirm skills |
| Job Matching | Match student skills with job requirements |
| Skill Gap | Identify missing skills and recommend training |
| Job Fair | Create fairs and register students |
| District Dashboard | View district-wise students, jobs, and skill gaps |

## 🗄️ Database Tables

- `students` — student profile and skills
- `jobs` — company job requirements
- `job_fairs` — job-fair details
- `fair_registrations` — student registrations for job fairs

## ▶️ How to Run

1. Install requirements:

```bash
pip install -r requirements.txt
```

2. Add your Neon PostgreSQL connection string in Streamlit Secrets:

```toml
DATABASE_URL = "your_neon_connection_string"
```

3. Run the app:

```bash
streamlit run app.py
```

## 📊 Demo Flow

1. Login as Student and create a profile
2. Upload or paste CV text
3. Confirm extracted skills
4. Login as Company and post a job
5. Open Job Matching
6. Select a job and student
7. View match score, matched skills, missing skills, and training recommendations
8. Login as Job Fair and register students
9. Open District Dashboard for analytics

## 🔮 Future Improvements

- Use real government and job-market datasets
- Add occupation-wise skill taxonomy
- Add GenAI policy copilot
- Add advanced district prioritisation scores
- Add role-based secure authentication
- Add Excel export along with CSV

## 👤 Developed By

Student project for Skill Gap and Emerging Skills Intelligence.
