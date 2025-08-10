import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

EXCEL_URL = "https://github.com/PythonPeters/Zweeds_woordenschat/raw/main/woorden.xlsx"

@st.cache_data
def laad_woordenlijst(url):
    return pd.read_excel(url, header=None, engine="openpyxl")

try:
    df = laad_woordenlijst(EXCEL_URL)
    df.columns = ["Zweeds", "Nederlands"]
except Exception as e:
    st.error(f"Kan woordenlijst niet laden van {EXCEL_URL}. Fout: {e}")
    st.stop()

def nieuw_woord():
    rij = df.sample().iloc[0]
    richting = st.session_state.get("richting", "Zweeds → Nederlands")
    if richting == "Zweeds → Nederlands":
        st.session_state["woord"] = rij["Zweeds"]
        st.session_state["juist"] = rij["Nederlands"]
    else:
        st.session_state["woord"] = rij["Nederlands"]
        st.session_state["juist"] = rij["Zweeds"]
    st.session_state["start_time"] = time.time()
    st.session_state["tijd_op"] = False
    st.session_state["feedback"] = ""
    st.session_state["kleur_feedback"] = None  # Geen kleur bij nieuw woord
    if "antwoord" in st.session_state:
        del st.session_state["antwoord"]

if "woord" not in st.session_state:
    st.session_state["score"] = 0
    st.session_state["richting"] = "Zweeds → Nederlands"
    st.session_state["refresh"] = False  # dummy key voor refresh
    nieuw_woord()

def controleer():
    if not st.session_state.get("tijd_op", False):
        antwoord = st.session_state.get("antwoord", "").strip().lower()
        juist = st.session_state.get("juist", "").strip().lower()
        if antwoord == juist and antwoord != "":
            st.session_state["kleur_feedback"] = "green"
            st.session_state["feedback"] = "✅ Goed!"
            if score_enabled:
                st.session_state["score"] += 1
        else:
            st.session_state["kleur_feedback"] = "red"
            st.session_state["feedback"] = f"❌ Fout! Juist was: {st.session_state.get('juist','')}"
            if score_enabled:
                st.session_state["score"] -= 1

st.title("🇸🇪 Zweeds Woordenschat Trainer")

st.session_state["richting"] = st.radio(
    "Kies richting",
    ["Zweeds → Nederlands", "Nederlands → Zweeds"],
    index=0
)

col1, col2 = st.columns(2)
with col1:
    score_enabled = st.checkbox("Score bijhouden", value=False)
with col2:
    timer_enabled = st.checkbox("Timer gebruiken", value=False)

timer_secs = 10
if timer_enabled:
    timer_secs = st.number_input("Aantal seconden per woord", min_value=3, max_value=60, value=10)

# Toon nieuw woord altijd in zwarte kleur, bovenaan in kader
st.markdown(
    f"""
    <div style="padding: 20px; border: 2px solid black; border-radius: 8px; background-color: #f0f0f0;">
        <h1 style="margin: 0; color: black;">
            Vertaal: {st.session_state.get('woord', '')}
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

if timer_enabled and st.session_state.get("start_time"):
    resterend = timer_secs - int(time.time() - st.session_state["start_time"])
    if resterend > 0:
        st.info(f"⏳ Tijd: {resterend} sec")
    else:
        if not st.session_state.get("tijd_op", False):
            st.session_state["kleur_feedback"] = "red"
            st.session_state["feedback"] = f"⏰ Tijd voorbij! Juist was: {st.session_state.get('juist','')}"
            if score_enabled:
                st.session_state["score"] -= 1
            st.session_state["tijd_op"] = True

# Antwoordveld
st.text_input(
    "Jouw vertaling:",
    value=st.session_state.get("antwoord", ""),
    key="antwoord",
    on_change=controleer
)

# Score
if score_enabled:
    st.write(f"**Score:** {st.session_state.get('score', 0)}")

# Knop nieuw woord met dummy refresh
if st.button("Nieuw woord"):
    nieuw_woord()
    st.session_state["refresh"] = not st.session_state.get("refresh", False)  # forceer her-render

# Feedback onderaan, met kleur en grotere tekst, alleen tonen als feedback er is
if st.session_state.get("feedback"):
    kleur = st.session_state.get("kleur_feedback", "black")
    st.markdown(
        f"<p style='font-size:20px; color: {kleur}; font-weight:bold;'>{st.session_state['feedback']}</p>",
        unsafe_allow_html=True
    )
