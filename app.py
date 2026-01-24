import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Student Career Counselling Dashboard", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#f7fbff,#fff8fc,#faf6ff);}
h1,h2,h3 { text-align:center; color:#2c3e50; }
.block-container { padding-top:0.8rem; }

.kpi-box{
    background: linear-gradient(135deg,#1abc9c,#16a085);
    padding:10px;
    border-radius:15px;
    color:white;
    text-align:center;
    font-size:14px;
    font-weight:600;
    box-shadow:0 3px 8px rgba(0,0,0,0.2);
}

/* Light filter boxes */
div[data-baseweb="select"] > div {
    background-color: #f1f6ff !important;
    border-radius: 6px;
    border: 1px solid #d6e4ff;
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 Student Career Counselling Dashboard")
# ================= GOOGLE SHEET =================
SHEET_ID = "1eXiH5-lACW7_x8VA7Fp7SQsBcW1uhf15Zy1AieU5wGE"
SHEET_NAME = "Sheet1"

@st.cache_data(ttl=60)
def load_data():
    encoded = quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded}"
    return pd.read_csv(url)

df = load_data()

# ================= AUTO COLUMN FINDER =================
def find_col(keyword):
    for c in df.columns:
        if keyword.lower() in c.lower():
            return c
    return None

COL_DISTRICT = find_col("district")
COL_SCHOOL   = find_col("school")
COL_CLASS    = find_col("class")
COL_GENDER   = find_col("gender")
COL_PREV     = find_col("previous")
COL_STREAM   = find_col("stream")

SUB1 = find_col("subject 1")
SUB2 = find_col("subject 2")
SUB3 = find_col("subject 3")

CII1 = find_col("cii")
CAR1 = find_col("career")
ENTRANCE = find_col("entrance")

# Clean base columns
for col in [COL_DISTRICT, COL_SCHOOL, COL_CLASS, COL_GENDER]:
    if col:
        df[col] = df[col].astype(str).str.strip()

# ================= FILTERS (WITHOUT HEADING) =================
f1, f2, f3 = st.columns(3)

with f1:
    district = st.selectbox("District", ["All"] + sorted(df[COL_DISTRICT].dropna().unique()))
with f2:
    school = st.selectbox("School", ["All"] + sorted(df[COL_SCHOOL].dropna().unique()))
with f3:
    class_name = st.selectbox("Class", ["All"] + sorted(df[COL_CLASS].dropna().unique()))

filtered_df = df.copy()
if district != "All":
    filtered_df = filtered_df[filtered_df[COL_DISTRICT] == district]
if school != "All":
    filtered_df = filtered_df[filtered_df[COL_SCHOOL] == school]
if class_name != "All":
    filtered_df = filtered_df[filtered_df[COL_CLASS] == class_name]

st.markdown("---")

# ================= KPI =================
k1, k2, k3, k4 = st.columns(4)

k1.markdown(f"<div class='kpi-box'>Students<br>{len(filtered_df)}</div>", unsafe_allow_html=True)
k2.markdown(f"<div class='kpi-box'>Schools<br>{filtered_df[COL_SCHOOL].nunique()}</div>", unsafe_allow_html=True)
k3.markdown(f"<div class='kpi-box'>Districts<br>{filtered_df[COL_DISTRICT].nunique()}</div>", unsafe_allow_html=True)

if COL_PREV:
    avg_prev = round(pd.to_numeric(filtered_df[COL_PREV], errors="coerce").mean(), 2)
else:
    avg_prev = "N/A"

k4.markdown(f"<div class='kpi-box'>Avg % Previous Class<br>{avg_prev}</div>", unsafe_allow_html=True)

st.markdown("---")

# ================= COLOR SYSTEM (DARK + LIGHT ALTERNATING) =================
DARK_COLORS = ["#0B5ED7", "#198754", "#6F42C1", "#DC3545", "#FD7E14"]
LIGHT_COLORS = ["#9EC5FE", "#A3CFBB", "#C5B3E6", "#F1AEB5", "#FFD8A8"]

def alternating_colors(n):
    colors = []
    for i in range(n):
        if i % 2 == 0:
            colors.append(DARK_COLORS[i % len(DARK_COLORS)])
        else:
            colors.append(LIGHT_COLORS[i % len(LIGHT_COLORS)])
    return colors

def style_fig(fig):
    fig.update_traces(textposition="outside", texttemplate="%{y}", cliponaxis=False)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.25,
                    xanchor="center", x=0.5, title_text=""),
        margin=dict(t=60, b=140, l=40, r=40),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# ================= STUDENT DISTRIBUTION =================
st.markdown("<h3>📍 Student Distribution</h3>", unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    dist_count = filtered_df[COL_DISTRICT].value_counts().reset_index()
    dist_count.columns = ["District", "Value"]
    fig = px.bar(
        dist_count, x="District", y="Value",
        color="District",
        text="Value",
        color_discrete_sequence=alternating_colors(len(dist_count)),
        title="District Wise Students"
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

with c2:
    gender_count = filtered_df[COL_GENDER].value_counts().reset_index()
    gender_count.columns = ["Gender", "Value"]
    fig = px.pie(
        gender_count, names="Gender", values="Value",
        title="Gender Ratio",
        color_discrete_sequence=alternating_colors(len(gender_count))
    )
    fig.update_traces(texttemplate="%{value} (%{percent})")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ================= SCHOOL & CLASS =================
st.markdown("<h3>🏫 School & Class Distribution</h3>", unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    school_count = filtered_df[COL_SCHOOL].value_counts().reset_index()
    school_count.columns = ["School", "Value"]
    fig = px.bar(
        school_count, x="School", y="Value",
        color="School",
        text="Value",
        color_discrete_sequence=alternating_colors(len(school_count)),
        title="School Wise Students"
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

with c4:
    temp = filtered_df.copy()
    temp["Class_clean"] = temp[COL_CLASS].astype(str).str.extract(r"(\d+)")
    temp = temp.dropna(subset=["Class_clean"])
    temp["Class_clean"] = temp["Class_clean"].astype(int)

    class_count = temp["Class_clean"].value_counts().reset_index()
    class_count.columns = ["Class", "Value"]
    class_count = class_count.sort_values(by="Class")
    class_count["Class_label"] = class_count["Class"].apply(lambda x: f"Class {x}")

    fig = px.bar(
        class_count, x="Class_label", y="Value",
        color="Class_label",
        text="Value",
        category_orders={"Class_label": class_count["Class_label"].tolist()},
        color_discrete_sequence=alternating_colors(len(class_count)),
        title="Class Wise Students"
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

st.markdown("---")

# ================= Career Interest Inventory =================
st.markdown("<h3>📑 Career Interest Inventory Test </h3>", unsafe_allow_html=True)

cii_data = []
if CII1:
    cii_data += filtered_df[CII1].dropna().astype(str).tolist()
cii_data = [x for x in cii_data if x.strip() != ""]

if cii_data:
    cii_count = pd.Series(cii_data).value_counts().reset_index()
    cii_count.columns = ["CII Result", "Students"]
    fig = px.bar(
        cii_count, x="CII Result", y="Students",
        color="CII Result",
        text="Students",
        color_discrete_sequence=alternating_colors(len(cii_count)),
        title="CII Test Results Distribution"
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

st.markdown("---")

# ================= CAREER DISTRIBUTION  =================
st.markdown("<h3>🎯 Career Distribution </h3>", unsafe_allow_html=True)

career_data = []
if CAR1:
    career_data += filtered_df[CAR1].dropna().astype(str).tolist()

career_data = [x.strip() for x in career_data if x.strip() != ""]

if career_data:
    career_count = pd.Series(career_data).value_counts().reset_index()
    career_count.columns = ["Career", "Students"]
    career_count = career_count.sort_values(by="Students", ascending=False).head(10)

    fig = px.bar(
        career_count, x="Career", y="Students",
        color="Career",
        text="Students",
        color_discrete_sequence=alternating_colors(len(career_count)),
        title="Top 10 Career Preferences (High to Low)"
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

st.markdown("---")

# ================= ENTRANCE EXAM =================
if ENTRANCE:
    ent = filtered_df[ENTRANCE].dropna().astype(str).tolist()
    ent = [x for x in ent if x.strip() != ""]
    if ent:
        ent_count = pd.Series(ent).value_counts().reset_index()
        ent_count.columns = ["Entrance Exam", "Students"]
        fig = px.bar(
            ent_count, x="Entrance Exam", y="Students",
            color="Entrance Exam",
            text="Students",
            color_discrete_sequence=alternating_colors(len(ent_count)),
            title="Entrance Examination Distribution"
        )
        st.plotly_chart(style_fig(fig), use_container_width=True)

st.markdown("---")

# ================= DOWNLOAD & TABLE =================
st.markdown("<h3>📥 Download Filtered Data</h3>", unsafe_allow_html=True)
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_students.csv", "text/csv")

st.markdown("<h3>📋 Student Data Table</h3>", unsafe_allow_html=True)
st.dataframe(filtered_df, use_container_width=True)

st.success("✅ Filters heading removed and all bar charts now show alternating dark & light colors for every bar.")
