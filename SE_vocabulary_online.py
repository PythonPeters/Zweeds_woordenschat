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
    st.session_state["kleur"] = "black"
    st.session_state["feedback"] = ""
    if "antwoord" in st.session_state:
        del st.session_state["antwoord"]
        st.session_state["feedback"] = ""
        st.session_state["kleur"] = "black"

if "woord" not in st.session_state:
    st.session_state["score"] = 0
    st.session_state["richting"] = "Zweeds → Nederlands"
    nieuw_woord()
    
def controleer():
    if not st.session_state.get("tijd_op", False):
        antwoord = st.session_state.get("antwoord", "").strip().lower()
        juist = st.session_state.get("juist", "").strip().lower()
        if antwoord == juist and antwoord != "":
            st.session_state["kleur"] = "green"
            st.session_state["feedback"] = "✅ Goed!"
            if score_enabled:
                st.session_state["score"] += 1
        else:
            st.session_state["kleur"] = "red"
            st.session_state["feedback"] = f"❌ Fout! Juist was: {st.session_state.get('juist','')}"
            if score_enabled:
                st.session_state["score"] -= 1

# dummy key voor refresh
dummy = st.session_state.get("refresh", False)

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

# Duidelijke weergave van het woord in een kader en groter lettertype
st.markdown(
    f"""
    <div style="padding: 20px; border: 2px solid {st.session_state.get('kleur', 'black')}; border-radius: 8px; background-color: #f9f9f9;">
        <h1 style="margin: 0; color: {st.session_state.get('kleur', 'black')};">
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
            st.session_state["kleur"] = "red"
            st.session_state["feedback"] = f"⏰ Tijd voorbij! Juist was: {st.session_state.get('juist','')}"
            if score_enabled:
                st.session_state["score"] -= 1
            st.session_state["tijd_op"] = True

st.text_input(
    "Jouw vertaling:",
    value=st.session_state.get("antwoord", ""),
    key="antwoord",
    on_change=controleer
)

# Feedback met grotere, duidelijke tekst en kleur
if st.session_state.get("feedback"):
    kleur_feedback = "green" if st.session_state.get("kleur") == "green" else "red"
    st.markdown(
        f"<p style='font-size:20px; color: {kleur_feedback}; font-weight:bold;'>{st.session_state['feedback']}</p>",
        unsafe_allow_html=True
    )

if score_enabled:
    st.write(f"**Score:** {st.session_state.get('score', 0)}")

if st.button("Nieuw woord"):
    nieuw_woord()
    st.session_state["refresh"] = not st.session_state.get("refresh", False)
