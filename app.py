import streamlit as st
import pandas as pd

st.set_page_config(page_title="KSISU Module 3", layout="wide")
st.title("KSISU Module 3: Skill Demand and Curriculum Gap Analysis")

uploaded = st.file_uploader("Upload Karnataka job postings CSV", type=["csv"])

if uploaded is None:
    st.info("Upload a CSV file containing job descriptions.")
    st.stop()

df = pd.read_csv(uploaded, dtype=str)

if df.empty:
    st.error("The uploaded CSV file is empty.")
    st.stop()

st.write("**Columns found in your CSV:**")
st.write(list(df.columns))

text_col = st.selectbox(
    "Select the column containing job descriptions",
    df.columns,
    index=0
)

text = " ".join(
    df[text_col]
    .dropna()
    .astype(str)
    .str.lower()
)

skill_dict = {
    "Excel": ["excel"],
    "SQL": ["sql"],
    "Python": ["python"],
    "Cloud computing": ["aws", "azure", "google cloud", "cloud"],
    "Linux": ["linux"],
    "Machine learning": ["machine learning", "ml"],
}

records = []
for skill, keywords in skill_dict.items():
    count = sum(text.count(keyword) for keyword in keywords)
    records.append({"Skill": skill, "Mentions": count})

skills_df = pd.DataFrame(records).sort_values("Mentions", ascending=False)

t1, t2 = st.tabs(["Skill demand", "Curriculum gap analysis"])

with t1:
    st.subheader("Skills found in job postings")
    st.bar_chart(skills_df.set_index("Skill"))
    st.dataframe(skills_df, use_container_width=True)

with t2:
    st.subheader("Enter your course baseline")

    course = st.text_input("Course name")
    syllabus = st.text_input("Syllabus reference / URL")
    covered = st.text_area(
        "Skills explicitly covered (comma separated)",
        "Excel, SQL"
    )

    covered_skills = [
        x.strip().lower()
        for x in covered.split(",")
        if x.strip()
    ]

    skills_df["Covered"] = skills_df["Skill"].str.lower().isin(covered_skills)

    total_mentions = skills_df["Mentions"].sum()
    covered_mentions = skills_df.loc[skills_df["Covered"], "Mentions"].sum()

    gap = 0 if total_mentions == 0 else 100 * (total_mentions - covered_mentions) / total_mentions

    st.metric("Mention-weighted coverage gap", f"{gap:.1f}%")
    st.dataframe(skills_df, use_container_width=True)

    missing = skills_df[
        (~skills_df["Covered"]) & (skills_df["Mentions"] > 0)
    ]

    st.write("**Topics to investigate for curriculum coverage:**")
    st.write(", ".join(missing["Skill"]) if not missing.empty else "None")

st.caption(
    "This app measures curriculum coverage against job-posting skill mentions. "
    "It is not a Karnataka worker-shortage, placement, or employability estimate."
)
