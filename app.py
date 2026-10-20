import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(
    page_title="Skill Gap Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("Skill Gap Analysis: Skill Demand and Curriculum Gap Analysis")
st.caption(
    "This tool analyses skills mentioned in uploaded Karnataka job postings and compares "
    "them with a course curriculum. It measures curriculum coverage, not worker shortage."
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
    "Communication": ["communication"],
}

# ---------------- File upload ----------------

uploaded_file = st.file_uploader(
    "Upload Karnataka job postings CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Please upload a CSV file containing job descriptions.")
    st.stop()

df = pd.read_csv(uploaded_file, dtype=str)

if df.empty:
    st.error("The uploaded CSV file is empty.")
    st.stop()

st.success(f"Uploaded {len(df)} job records.")

st.write("**Columns found in your CSV:**")
st.write(list(df.columns))

text_col = st.selectbox(
    "Select the column containing job descriptions",
    df.columns,
    index=0
)

job_text = (
    df[text_col]
    .dropna()
    .astype(str)
    .str.lower()
    .tolist()
)

# ---------------- Skill extraction ----------------

def extract_skills(text):
    found = []
    for skill, keywords in SKILL_DICT.items():
        for keyword in keywords:
            if keyword in text:
                found.append(skill)
                break
    return found

skill_counts = Counter()
occupation_skill_counts = Counter()
co_occurrence = Counter()

for text in job_text:
    skills = extract_skills(text)

    for skill in skills:
        skill_counts[skill] += 1

    for skill in skills:
        occupation_skill_counts[(text_col, skill)] += 1

    for i in range(len(skills)):
        for j in range(i + 1, len(skills)):
            pair = tuple(sorted([skills[i], skills[j]]))
            co_occurrence[pair] += 1

skills_df = pd.DataFrame(
    [(skill, count) for skill, count in skill_counts.items()],
    columns=["Skill", "Mentions"]
).sort_values("Mentions", ascending=False)

if skills_df.empty:
    st.warning("No recognised skills were found in the selected column.")
    st.stop()

# ---------------- Tabs ----------------

t1, t2, t3, t4 = st.tabs([
    "Skill demand",
    "Occupation mapping",
    "Co-occurrence",
    "Curriculum gap analysis"
])

# ---------------- Tab 1: Skill demand ----------------

with t1:
    st.subheader("Skill demand in uploaded job postings")

    st.bar_chart(skills_df.set_index("Skill"))

    st.dataframe(
        skills_df,
        use_container_width=True
    )

    st.info(
        "Higher mention counts indicate more frequent demand in this uploaded sample. "
        "They do not prove statewide labour-market demand."
    )

# ---------------- Tab 2: Occupation mapping ----------------

with t2:
    st.subheader("Occupation mapping")

    st.write(
        "This table shows how often each recognised skill appears across the uploaded job records."
    )

    occupation_df = skills_df.copy()
    occupation_df["Share of records mentioning skill"] = (
        occupation_df["Mentions"] / len(job_text) * 100
    ).round(1)

    occupation_df["Share of records mentioning skill"] = (
        occupation_df["Share of records mentioning skill"].astype(str) + "%"
    )

    st.dataframe(
        occupation_df,
        use_container_width=True
    )

    st.caption(
        "Job postings are used as a proxy for occupational skill requirements. "
        "A posting may mention multiple skills."
    )

# ---------------- Tab 3: Co-occurrence ----------------

with t3:
    st.subheader("Skill co-occurrence")

    if co_occurrence:
        co_df = pd.DataFrame(
            [(a, b, count) for (a, b), count in co_occurrence.items()],
            columns=["Skill 1", "Skill 2", "Jobs mentioning both"]
        ).sort_values("Jobs mentioning both", ascending=False)

        st.dataframe(
            co_df,
            use_container_width=True
        )

        st.bar_chart(
            co_df.set_index(["Skill 1", "Skill 2"])
        )
    else:
        st.info("No skill pairs were found in the uploaded job descriptions.")

# ---------------- Tab 4: Curriculum gap ----------------

with t4:
    st.subheader("Which observed job skills are missing from a course baseline?")

    st.write(
        "This calculates curriculum coverage, not Karnataka’s worker shortage. "
        "Job data alone cannot establish worker supply."
    )

    baseline_type = st.text_input(
        "Baseline type",
        value="Illustrative demo baseline"
    )

    course_name = st.text_input("Course name")
    syllabus_url = st.text_input("Syllabus reference / URL")

    covered_input = st.text_area(
        "Skills explicitly covered",
        value="Excel, SQL"
    )

    submitted = st.button(
        "I have finished entering coverage from the referenced syllabus"
    )

    covered_skills = [
        x.strip().lower()
        for x in covered_input.split(",")
        if x.strip()
    ]

    gap_df = skills_df.copy()
    gap_df["Covered"] = gap_df["Skill"].str.lower().isin(covered_skills)

    total_mentions = gap_df["Mentions"].sum()
    covered_mentions = gap_df.loc[gap_df["Covered"], "Mentions"].sum()

    if total_mentions > 0:
        coverage_gap = 100 * (total_mentions - covered_mentions) / total_mentions
    else:
        coverage_gap = 0

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Skills not listed",
        f"{int((~gap_df['Covered']).sum())} / {len(gap_df)}"
    )

    col2.metric(
        "Skills listed",
        f"{int(gap_df['Covered'].sum())} / {len(gap_df)}"
    )

    col3.metric(
        "Mention-weighted coverage gap",
        f"{coverage_gap:.1f}%"
    )

    missing_skills = gap_df[
        (~gap_df["Covered"]) & (gap_df["Mentions"] > 0)
    ]["Skill"].tolist()

    st.write("**Topics to investigate for curriculum coverage:**")
    st.write(", ".join(missing_skills) if missing_skills else "None")

    st.info(
        "Not listed does not mean no training or skilled workers exist. "
        "Covered does not verify proficiency. The starter dictionary may miss some skills "
        "and does not separate mandatory from optional mentions."
    )

    st.subheader("Calculation and interpretation")

    if total_mentions > 0:
        st.write(
            f"{total_mentions - covered_mentions} unlisted record–skill mentions / "
            f"{total_mentions} total recognised record–skill mentions × 100 = "
            f"{coverage_gap:.1f}%."
        )
    else:
        st.write("No recognised skill mentions were found in the uploaded data.")

    st.write(
        "A record can mention several skills. This score measures mention-weighted coverage "
        "of this sample against the entered baseline only. It is not a shortage, placement, "
        "or employability percentage."
    )

    st.subheader("Selected source coverage")
    st.dataframe(
        gap_df,
        use_container_width=True
    )
