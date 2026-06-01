import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# ====================== CONFIG ======================
DATA_FILE = "crohns_stowing_log.json"

st.set_page_config(
    page_title="Crohn’s Stower Tracker",
    page_icon="🦠",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🦠 Crohn’s Disease Stower Tracker")
st.markdown("**Amazon WMN7 RAT+ Edition** — Quick daily symptom logging")

# ====================== LOAD / SAVE ======================
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_json(DATA_FILE, orient="records")
        df["date"] = pd.to_datetime(df["date"])
        return df
    return pd.DataFrame()

def save_entry(entry):
    df = load_data()
    new_row = pd.DataFrame([entry])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_json(DATA_FILE, orient="records", date_format="iso")
    st.success("✅ Entry saved!")
    st.rerun()  # Refresh to show new data immediately

# ====================== COPY TO CLIPBOARD HELPERS ======================
def copy_to_clipboard(text: str, label: str):
    # JavaScript copy
    js = f"""
    <script>
    function copyText() {{
        navigator.clipboard.writeText(`{text}`).then(() => {{
            alert("✅ Copied {label} to clipboard!");
        }});
    }}
    copyText();
    </script>
    """
    st.components.v1.html(js, height=0)

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
    entry = {
        "date": str(date),
        "shift": shift,
        "pain": pain,
        "urgency": urgency,
        "fatigue": fatigue,
        "joint_pain": joint,
        "hydration": hydration,
        "flare_risk": flare,
        "rate_impact": rate_impact,
        "notes": notes
    }
    save_entry(entry)

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
                   "joint_pain", "hydration", "flare_risk", "rate_impact"]],
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

    # ====================== COPY BUTTONS ======================
    st.subheader("📋 Copy Logs to Clipboard")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("📄 Copy as CSV", use_container_width=True):
            csv_text = df.to_csv(index=False)
            copy_to_clipboard(csv_text.replace("`", "'"), "CSV")
    
    with col_b:
        if st.button("🔧 Copy as JSON", use_container_width=True):
            json_text = df.to_json(orient="records", date_format="iso", indent=2)
            copy_to_clipboard(json_text.replace("`", "'"), "JSON")

else:
    st.info("No entries yet. Log your first day above.")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Tips for Crohn’s Stowers")
    st.markdown("""
    - Log daily at end of shift  
    - Use copied logs for doctor visits or Amazon accommodations  
    - Paste CSV directly into Google Sheets/Excel  
    """)
    
    if st.button("🗑️ Clear All Data"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("All data cleared")
            st.rerun()
