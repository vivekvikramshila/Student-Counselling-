# ==========================================================
# Career Guidance & Counseling Dashboard
# FULL VERSION – NORMAL A4 PRINT
# ==========================================================

import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import os

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(
    page_title=" Dashboard of Counselling of Students",
    layout="wide",
    page_icon="📊"
)

CHART_HEIGHT = 400
FONT_SIZE = 12
COLORS = ["#1f77b4", "#ff7f0e", "#fff2b2", "#b6e3c6"]

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
h1, h2 = st.columns([1, 6])
with h1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)

with h2:
    st.markdown(
        "<h1 style='text-align:center;color:#0b3c91;'>Dashboard of Counselling of Students</h1>",
        unsafe_allow_html=True
    )

# ----------------------------------------------------------
# TITLE BOX
# ----------------------------------------------------------
def box_title(text):
    st.markdown(
        f"""
        <div style="background:#f2f2f2;padding:10px;border-radius:8px;
        text-align:center;font-weight:700;font-size:20px;
        border:1px solid #ccc;margin-bottom:10px;">
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
    url = "https://docs.google.com/spreadsheets/d/1eXiH5-lACW7_x8VA7Fp7SQsBcW1uhf15Zy1AieU5wGE/export?format=csv"
    return pd.read_csv(url).dropna(how="all")

df = load_data()

for c in df.columns:
    df[c] = (
        df[c].astype(str)
        .str.strip()
        .replace(["nan", "NaN", "None", "undefined", ""], pd.NA)
    )

# ----------------------------------------------------------
# FILTERS
# ----------------------------------------------------------
f1, f2 = st.columns(2)
with f1:
    district = st.selectbox(
        "District",
        ["All"] + sorted(df["District"].dropna().unique())
    )
with f2:
    schools = (
        df["School"].dropna().unique()
        if district == "All"
        else df[df["District"] == district]["School"].dropna().unique()
    )
    school = st.selectbox("School", ["All"] + sorted(schools))

fdf = df.copy()
if district != "All":
    fdf = fdf[fdf["District"] == district]
if school != "All":
    fdf = fdf[fdf["School"] == school]

TOTAL = len(fdf)


# ----------------------------------------------------------
# KPI SECTION
# ----------------------------------------------------------
box_title("Key Performance Indicators")
k1, k2, k3, k4 = st.columns(4)

def kpi_big(title, value, color):
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;">
            <div style="
                background:{color};
                width:120px;height:120px;border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                color:white;font-size:26px;font-weight:700;">
                {value}
            </div>
            <div style="margin-top:8px;font-weight:700;font-size:16px;">
                {title}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k1: kpi_big("Students", TOTAL, COLORS[0])
with k2: kpi_big("Districts", fdf["District"].nunique(), COLORS[1])
with k3: kpi_big("Schools", fdf["School"].nunique(), COLORS[0])
with k4: kpi_big("Classes", fdf["Class"].nunique(), COLORS[1])

st.markdown("---")

# ----------------------------------------------------------
# COMMON BAR STYLE
# ----------------------------------------------------------
def bar_style(fig):
    fig.update_traces(
        texttemplate="%{customdata[0]} (%{customdata[1]}%)",
        textposition="outside",
        cliponaxis=False,
        textfont=dict(size=FONT_SIZE)
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=dict(l=30, r=20, t=40, b=70),
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0.5,
            xanchor="center",
            title_text=""
        ),
        xaxis_title="",
        yaxis_title=""
    )
    return fig
# ==========================================================
# ROW 1 → GENDER + DISTRICT GENDER
# ==========================================================
c1, c2 = st.columns(2)

with c1:
    box_title("Gender-wise Students (%)")
    g = fdf["Gender"].dropna().value_counts().reset_index()
    g.columns = ["Gender", "Count"]
    g["Percentage"] = (g["Count"] / TOTAL * 100).round(1)

    fig = px.pie(
        g,
        names="Gender",
        values="Percentage",
        hole=0.4,
        color_discrete_sequence=[COLORS[1], COLORS[0]]
    )
    fig.update_layout(height=CHART_HEIGHT,
        legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    box_title("District-wise Gender Distribution (%)")
    dg = fdf.groupby(["District", "Gender"]).size().reset_index(name="Count")
    dg["Percentage"] = (
        dg.groupby("District")["Count"]
        .transform(lambda x: round(x / x.sum() * 100, 1))
    )

    fig = px.bar(
        dg,
        x="District",
        y="Percentage",
        color="Gender",
        custom_data=["Count", "Percentage"],
        barmode="group",
        color_discrete_sequence=COLORS
    )
    st.plotly_chart(bar_style(fig), use_container_width=True)

st.markdown("---")

# ==========================================================
# ROW 2 → CLASS + STREAM
# ==========================================================
c1, c2 = st.columns(2)

with c1:
    box_title("Class-wise Students (%)")
    cl = fdf["Class"].dropna().value_counts().reset_index()
    cl.columns = ["Class", "Count"]
    cl["Percentage"] = (cl["Count"] / TOTAL * 100).round(1)

    fig = px.bar(
        cl,
        x="Class",
        y="Percentage",
        custom_data=["Count", "Percentage"],
        color="Class",
        color_discrete_sequence=COLORS
    )
    st.plotly_chart(bar_style(fig), use_container_width=True)

with c2:
    box_title("Stream-wise Students (%)")
    st_df = fdf["Stream"].dropna().value_counts().reset_index()
    st_df.columns = ["Stream", "Count"]
    st_df["Percentage"] = (st_df["Count"] / st_df["Count"].sum() * 100).round(1)

    fig = px.bar(
        st_df,
        x="Stream",
        y="Percentage",
        custom_data=["Count", "Percentage"],
        color="Stream",
        color_discrete_sequence=COLORS
    )
    st.plotly_chart(bar_style(fig), use_container_width=True)

st.markdown("---")

# ==========================================================
# ROW 3 → SUBJECT + CII
# ==========================================================
c1, c2 = st.columns(2)

with c1:
    box_title("Subject-wise Distribution (%)")

    subj_vals = []
    for col in ["Subject 1", "Subject 2", "Subject 3"]:
        if col in fdf.columns:
            subj_vals.extend(fdf[col].dropna().tolist())

    subj = pd.Series(subj_vals).value_counts().reset_index()
    subj.columns = ["Subject", "Count"]
    subj["Percentage"] = (subj["Count"] / subj["Count"].sum() * 100).round(1)

    fig = px.bar(
        subj,
        x="Subject",
        y="Percentage",
        custom_data=["Count", "Percentage"],
        color="Subject",
        color_discrete_sequence=COLORS
    )

    fig = bar_style(fig)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    box_title("CII – Career Interest Distribution (%)")

    cii_vals = []
    for col in ["CII-1", "CII-2", "CII-3"]:
        if col in fdf.columns:
            cii_vals.extend(fdf[col].dropna().tolist())

    cii = pd.Series(cii_vals).value_counts().reset_index()
    cii.columns = ["Interest Area", "Count"]
    cii["Percentage"] = (cii["Count"] / cii["Count"].sum() * 100).round(1)

    fig = px.bar(
        cii,
        x="Interest Area",
        y="Percentage",
        custom_data=["Count", "Percentage"],
        color="Interest Area",
        color_discrete_sequence=COLORS
    )

    fig = bar_style(fig)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================================
# ROW 4 → CLASS 10 & 12
# ==========================================================
box_title("District-wise Class 10th & 12th Students (Gender-wise)")

def class_gender_chart(cls):
    d = (
        fdf[fdf["Class"] == cls]
        .groupby(["District", "Gender"])
        .size()
        .reset_index(name="Count")
    )

    d["Percentage"] = (
        d.groupby("District")["Count"]
        .transform(lambda x: round(x / x.sum() * 100, 1))
    )

    fig = px.bar(
        d,
        x="District",
        y="Count",
        color="Gender",
        barmode="group",
        custom_data=["Count", "Percentage"],
        color_discrete_sequence=COLORS
    )

    fig = bar_style(fig)

    # Show Count + Percentage above bar
    fig.update_traces(
        texttemplate="%{customdata[0]} (%{customdata[1]}%)",
        textposition="outside"
    )

    return fig

c1, c2 = st.columns(2)
with c1:
    st.markdown("<h3 style='text-align:center;'>Class 10th</h3>", unsafe_allow_html=True)
    st.plotly_chart(class_gender_chart("10"), use_container_width=True)

with c2:
    st.markdown("<h3 style='text-align:center;'>Class 12th</h3>", unsafe_allow_html=True)
    st.plotly_chart(class_gender_chart("12"), use_container_width=True)

st.markdown("---")

# ==========================================================
# DISTRICT SUMMARY TABLE
# ==========================================================
box_title("District-wise Summary (Class 10 & 12)")

districts = fdf["District"].dropna().unique()
summary = pd.DataFrame({"District": districts})

def count_val(cls, gen):
    return (
        fdf[(fdf["Class"] == cls) & (fdf["Gender"] == gen)]
        .groupby("District")
        .size()
        .reset_index(name=f"Class {cls} {gen}")
    )

for cls in ["10", "12"]:
    for gen in ["Male", "Female"]:
        summary = summary.merge(count_val(cls, gen), on="District", how="left")

summary = summary.fillna(0)

summary["Total Students (10+12)"] = (
    summary[["Class 10 Male", "Class 10 Female", "Class 12 Male", "Class 12 Female"]]
    .sum(axis=1)
)

for col in ["Class 10 Male", "Class 10 Female", "Class 12 Male", "Class 12 Female"]:
    summary[col + " (%)"] = (
        summary[col] / summary["Total Students (10+12)"] * 100
    ).round(1)

summary.index += 1
summary.index.name = "Sr No"
st.dataframe(summary, use_container_width=True)








