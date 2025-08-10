import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

# GITHUB_EXCEL_URL = "https://github.com/PythonPeters/Zweeds_woordenschat/raw/main/woorden.xlsx"
GITHUB_EXCEL_URL = "https://github.com/PythonPeters/Zweeds_woordenschat/blob/main/woorden.xlsx"

@st.cache_data
def laad_woordenlijst(url):
    return pd.read_excel(url, header=None, engine="openpyxl")

try:
    df = laad_woordenlijst(GITHUB_EXCEL_URL)
    df.columns = ["Zweeds", "Nederlands"]
except Exception as e:
    st.error(f"Kan woordenlijst niet laden vanaf GitHub: {e}")
    st.stop()

richting = st.radio(
    "Kies richting",
    ["Zweeds → Nederlands", "Nederlands → Zweeds"]
)

col1, col2 = st.columns(2)
with col1:
    score_enabled = st.checkbox("Score bijhouden", value=False)
with col2:
    timer_enabled = st.checkbox("Timer gebruiken", value=False)

timer_secs = 10
if timer_enabled:
    timer_secs = st.number_input("Aantal seconden per woord", min_value=3, max_value=60, value=10)

# Sessiestate initiëren
if "woord" not in st.session_state:
    st.session_state.woord = None
    st.session_state.juist = None
    st.session_state.score = 0
    st.session_state.start_time = None
    st.session_state.tijd_op = False
    st.session_state.antwoord = ""
    st.session_state.feedback = ""

def nieuw_woord():
    rij = df.sample().iloc[0]
    if richting == "Zweeds → Nederlands":
        st.session_state.woord = rij["Zweeds"]
        st.session_state.juist = rij["Nederlands"]
    else:
        st.session_state.woord = rij["Nederlands"]
        st.session_state.juist = rij["Zweeds"]
    st.session_state.start_time = time.time()
    st.session_state.tijd_op = False
    st.session_state.antwoord = ""
    st.session_state.feedback = ""

if st.button("Nieuw woord"):
    nieuw_woord()

# Controlefunctie buiten de on_change callback gezet om te kunnen aanroepen na Enter
def controleer(antwoord):
    if not st.session_state.tijd_op and antwoord.strip() != "":
        if antwoord.strip().lower() == st.session_state.juist.lower():
            st.session_state.feedback = "✅ Juist!"
            if score_enabled:
                st.session_state.score += 1
        else:
            st.session_state.feedback = f"❌ Fout. Juist was: {st.session_state.juist}"
            if score_enabled:
                st.session_state.score -= 1

# Woord tonen
if st.session_state.woord:
    st.subheader(f"Vertaal: **{st.session_state.woord}**")

    if timer_enabled and st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
        resterend = timer_secs - elapsed
        if resterend > 0:
            st.info(f"⏳ Tijd: {resterend} sec")
        else:
            if not st.session_state.tijd_op:
                st.warning(f"⏰ Tijd voorbij! Juist was: **{st.session_state.juist}**")
                if score_enabled:
                    st.session_state.score -= 1
                st.session_state.tijd_op = True

    antwoord = st.text_input(
        "Jouw vertaling:",
        value=st.session_state.antwoord,
        key="antwoord",
        on_change=lambda: controleer(st.session_state.antwoord)
    )

    if "feedback" in st.session_state and st.session_state.feedback != "":
        if st.session_state.feedback.startswith("✅"):
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)

    if score_enabled:
        st.write(f"**Score:** {st.session_state.score}")

else:
    st.info("⬆️ Klik op 'Nieuw woord' om te beginnen.")

