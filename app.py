# ==========================================================
# COMPLETE STUDENT COUNSELLING DASHBOARD (ONE FILE)
# KPI → Colored Circle (Center)
# Gender → Pie Chart (Blue & Orange)
# All Charts → Blue, Orange, Light Yellow, Light Orange
# District-wise Gender Added
# 1 Row = 2 Charts
# Legends → Bottom & Center
# KPI in Circle
# Logo → Top Left
# Footer → Bottom Center (Vikramshila Education Resource Society)
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from PIL import Image

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(
    page_title="Student Career Counselling Dashboard",
    layout="wide",
    page_icon="📊"
)

# ----------------------------------------------------------
# LOGO + TITLE HEADER
# ----------------------------------------------------------
header_col1, header_col2 = st.columns([1,6])

with header_col1:
    # Put your logo file in same folder and name it: logo.png
    logo = Image.open("logo.png")
    st.image(logo, width=120)

with header_col2:
    st.markdown(
        "<h1 style='text-align:center;'>Student Career Counselling Dashboard</h1>",
        unsafe_allow_html=True
    )

# ----------------------------------------------------------
# TITLE BOX FUNCTION
# ----------------------------------------------------------
def box_title(text):
    st.markdown(
        f"""
        <div style="
            background:#f2f2f2;
            padding:10px;
            border-radius:8px;
            text-align:center;
            font-weight:700;
            font-size:20px;
            border:1px solid #ccc;
            margin-bottom:10px;">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read()
    if data is None:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df = df.dropna(how="all")
    return df

df = load_data()

if df.empty:
    st.error("Google Sheet se data load nahi ho raha hai.")
    st.stop()

# ----------------------------------------------------------
# CLEANING
# ----------------------------------------------------------
text_cols = [
    "District","School","Gender","Class","Stream",
    "CII-1","CII-2","CII-3",
    "Suggest Career Path-1","Suggest Career Path-2","Suggest Career Path-3",
    "Entrance Examination -1","Entrance Examination -2","Entrance Examination -3"
]

for c in text_cols:
    if c in df.columns:
        df[c] = (
            df[c].astype(str)
            .str.strip()
            .replace(["nan","NaN","None",""], pd.NA)
        )

# Remove undefined values everywhere
df = df.replace(["undefined", "Undefined", "UNDEFINED", ""], pd.NA)

# ----------------------------------------------------------
# COLORS
# ----------------------------------------------------------
COLORS = ["#1f77b4", "#ff7f0e", "#fff2b2", "#ffd8a8"]

# ----------------------------------------------------------
# KPI (CIRCLE STYLE)
# ----------------------------------------------------------
box_title("Key Performance Indicators")

k1, k2, k3, k4 = st.columns(4)

def kpi_circle(title, value, color):
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;">
            <div style="
                background:{color};
                width:110px;
                height:110px;
                border-radius:50%;
                display:flex;
                align-items:center;
                justify-content:center;
                color:white;
                font-size:26px;
                font-weight:700;">
                {value}
            </div>
            <div style="margin-top:6px;font-weight:600;">{title}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k1: kpi_circle("Students", len(df), "#1f77b4")
with k2: kpi_circle("Districts", df["District"].nunique(), "#ff7f0e")
with k3: kpi_circle("Schools", df["School"].nunique(), "#1f77b4")
with k4: kpi_circle("Classes", df["Class"].nunique(), "#ff7f0e")

st.markdown("---")

# ==========================================================
# ROW 1 → Gender Pie + District-wise Gender
# ==========================================================
c1, c2 = st.columns(2)

with c1:
    box_title("Gender-wise Student Distribution")

    gender_df = df["Gender"].dropna().value_counts().reset_index()
    gender_df.columns = ["Gender", "Students"]

    fig = px.pie(
        gender_df,
        names="Gender",
        values="Students",
        hole=0.4,
        color_discrete_sequence=["#ff7f0e", "#1f77b4"]
    )
    fig.update_layout(
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    box_title("District-wise Gender Distribution")

    dg = df.dropna(subset=["District","Gender"]).groupby(
        ["District","Gender"]
    ).size().reset_index(name="Students")

    fig = px.bar(
        dg,
        x="District",
        y="Students",
        color="Gender",
        barmode="group",
        text="Students",
        color_discrete_sequence=COLORS
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        xaxis_title="",        # Remove "District" text
        yaxis_title="",        # Optional: remove Y axis label
        bargap=0.25,           # Space between districts
        bargroupgap=0.1,       # Space between gender bars
        legend=dict(
            orientation="h",
            y=-0.35,
            x=0.5,
            xanchor="center",
            title_text=""      # Remove "Gender" heading
        ),
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)
st.markdown("---")

# ==========================================================
# ROW 2 → Class-wise + CII
# ==========================================================
c1, c2 = st.columns(2)

with c1:
    box_title("Class-wise Student Count")

    class_df = df["Class"].dropna().value_counts().reset_index()
    class_df.columns = ["Class", "Students"]

    fig = px.bar(
        class_df,
        x="Class",
        y="Students",
        color="Class",
        text="Students",
        color_discrete_sequence=COLORS
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0.5,
            xanchor="center",
            title_text=""
        )
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    box_title("CII Test – Career Interest Distribution")

    cii_vals = []
    for c in ["CII-1","CII-2","CII-3"]:
        if c in df.columns:
            cii_vals.extend(df[c].dropna().tolist())

    if cii_vals:
        df_cii = pd.Series(cii_vals).value_counts().reset_index()
        df_cii.columns = ["Interest Area", "Students"]

        fig = px.bar(
            df_cii,
            x="Interest Area",
            y="Students",
            color="Interest Area",
            text="Students",
            color_discrete_sequence=COLORS
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            legend=dict(orientation="h", y=-0.4, x=0.5, xanchor="center")
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================================
# ROW 3 → Career Path + Entrance Exam
# ==========================================================
c1, c2 = st.columns(2)

with c1:
    box_title("Top 10 Suggested Career Paths")

    cp_vals = []
    for c in ["Suggest Career Path-1","Suggest Career Path-2","Suggest Career Path-3"]:
        if c in df.columns:
            cp_vals.extend(df[c].dropna().tolist())

    if cp_vals:
        df_cp = pd.Series(cp_vals).value_counts().head(10).reset_index()
        df_cp.columns = ["Career Path", "Students"]

        fig = px.bar(
            df_cp,
            x="Career Path",
            y="Students",
            color="Career Path",
            text="Students",
            color_discrete_sequence=COLORS
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            legend=dict(orientation="h", y=-0.45, x=0.5, xanchor="center")
        )
        st.plotly_chart(fig, use_container_width=True)

with c2:
    box_title("Entrance Examination Preferences")

    ee_vals = []
    for c in ["Entrance Examination -1","Entrance Examination -2","Entrance Examination -3"]:
        if c in df.columns:
            ee_vals.extend(df[c].dropna().tolist())

    if ee_vals:
        df_ee = pd.Series(ee_vals).value_counts().reset_index()
        df_ee.columns = ["Entrance Exam", "Students"]

        fig = px.bar(
            df_ee,
            x="Entrance Exam",
            y="Students",
            color="Entrance Exam",
            text="Students",
            color_discrete_sequence=COLORS
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            legend=dict(orientation="h", y=-0.45, x=0.5, xanchor="center")
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================================
# FULL DATA TABLE
# ==========================================================
box_title("Complete Student Data Table")
st.dataframe(df, use_container_width=True)

# ----------------------------------------------------------
# FOOTER (BOTTOM CENTER)
# ----------------------------------------------------------
st.markdown(
    """
    <div style="
        position:fixed;
        left:0;
        bottom:0;
        width:100%;
        background:#f2f2f2;
        text-align:center;
        padding:8px;
        font-weight:600;
        border-top:1px solid #ccc;">
        © Vikramshila Education Resource Society
    </div>
    """,
    unsafe_allow_html=True
)
