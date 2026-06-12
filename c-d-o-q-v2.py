import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Crohn’s Stower Tracker",
    page_icon="🦠",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🦠 Crohn’s Disease Stower Tracker")
st.markdown("**Amazon WMN7 RAT+ Edition** — Quick daily symptom logging")

# ====================== DATA SOURCE ======================
CSV_URL = "https://raw.githubusercontent.com/BurstSoftware/C-d-o-q-v1/main/crohns-data-61226.csv"

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df["date"] = pd.to_datetime(df["date"])
        # Ensure correct column order and types
        df = df[["date", "shift", "pain", "urgency", "fatigue", 
                "joint_pain", "hydration", "flare_risk"]]
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame(columns=["date", "shift", "pain", "urgency", "fatigue", 
                                   "joint_pain", "hydration", "flare_risk"])

# ====================== MAIN FORM ======================
with st.form("daily_log"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", datetime.today())
    with col2:
        shift = st.text_input("Shift Type", value="RAT+", help="e.g. RAT+, MET, 10hr")

    st.subheader("Symptom Scores (1 = Excellent → 5 = Debilitating)")

    pain = st.slider("1. Abdominal Pain / Cramping", 1, 5, 1)
    urgency = st.slider("2. Bowel Urgency / Frequency", 1, 5, 1)
    fatigue = st.slider("3. Fatigue / Energy Level", 1, 5, 1)
    joint = st.slider("4. Joint or Back Pain", 1, 5, 1)
    hydration = st.slider("5. Hydration Status", 1, 5, 1, 
                         help="1 = Well hydrated, 5 = Very dehydrated")
    flare = st.slider("6. Overall Flare Risk", 1, 5, 1)

    rate_impact = st.slider("7. Stowing Rate Impact (% of normal)", 0, 100, 85)
    notes = st.text_area("8. Notes / Triggers", placeholder="Heat, heavy totes, missed meds...")

    submitted = st.form_submit_button("Save Today's Log", type="primary")

if submitted:
    # For now, just show success (you can extend this to append to GitHub later if needed)
    st.success("✅ Entry logged! (Note: This version currently reads from GitHub CSV only)")
    st.info("To permanently save new entries, consider switching to a backend (Google Sheets, Supabase, etc.)")

# ====================== HISTORY & CHARTS ======================
st.divider()
st.subheader("📊 Your Log History")

df = load_data()

if not df.empty:
    display_df = df.copy()
    display_df["date"] = display_df["date"].dt.date
    display_df = display_df.sort_values("date", ascending=False)
    
    st.dataframe(
        display_df[["date", "shift", "pain", "urgency", "fatigue", 
                   "joint_pain", "hydration", "flare_risk"]],
        use_container_width=True,
        hide_index=True
    )

    # Charts
    st.subheader("Trend Over Time")
    chart_df = df.set_index("date")[["pain", "urgency", "fatigue", "joint_pain", "hydration", "flare_risk"]]
    st.line_chart(chart_df, height=400)

    # Summary
    avg_score = round(df[["pain","urgency","fatigue","joint_pain","hydration","flare_risk"]].mean().mean(), 1)
    st.metric("Average Score", f"{avg_score}/5")
    
    if avg_score >= 4.0:
        st.error("🚨 High risk — consider FMLA/ADA discussion")
    elif avg_score >= 3.0:
        st.warning("⚠️ Moderate — keep monitoring")

    # Copy buttons
    st.subheader("📋 Copy Logs to Clipboard")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("📄 Copy as CSV", use_container_width=True):
            csv_text = df.to_csv(index=False)
            st.code(csv_text, language="csv")
            st.caption("Copy the text above 👆")
    
    with col_b:
        if st.button("🔧 Copy as JSON", use_container_width=True):
            json_text = df.to_json(orient="records", date_format="iso", indent=2)
            st.code(json_text, language="json")
            st.caption("Copy the text above 👆")

else:
    st.info("No data available from the CSV.")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Tips for Crohn’s Stowers")
    st.markdown("""
    - Data is loaded from GitHub raw CSV  
    - New entries are shown temporarily (not yet saved back)  
    - Paste copied CSV directly into Google Sheets/Excel  
    """)
    
    st.info(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
