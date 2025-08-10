import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

# RAW GitHub link naar jouw Excel
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

# --- Functie nieuw woord ---
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
    # VEILIGE blanking van het tekstveld: verwijder de key als die bestaat
    if "antwoord" in st.session_state:
        del st.session_state["antwoord"]

# --- Init session state ---
if "woord" not in st.session_state:
    st.session_state["score"] = 0
    st.session_state["richting"] = "Zweeds → Nederlands"
    nieuw_woord()

# --- Controlefunctie ---
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

# --- UI ---
st.title("🇸🇪 Zweeds Woordenschat Trainer")

# Richting
st.session_state["richting"] = st.radio(
    "Kies richting",
    ["Zweeds → Nederlands", "Nederlands → Zweeds"],
    index=0
)

# Opties (standaard uit)
col1, col2 = st.columns(2)
with col1:
    score_enabled = st.checkbox("Score bijhouden", value=False)
with col2:
    timer_enabled = st.checkbox("Timer gebruiken", value=False)

# Timer-instelling
timer_secs = 10
if timer_enabled:
    timer_secs = st.number_input("Aantal seconden per woord", min_value=3, max_value=60, value=10)

# Toon woord (met kleur)
st.markdown(
    f"<h2 style='color:{st.session_state.get('kleur','black')};'>Vertaal: {st.session_state.get('woord','')}</h2>",
    unsafe_allow_html=True
)

# Timer gedrag
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

# Antwoordveld (veilig: gebruik get)
st.text_input(
    "Jouw vertaling:",
    value=st.session_state.get("antwoord", ""),
    key="antwoord",
    on_change=controleer
)

# Feedback + score
if st.session_state.get("feedback"):
    st.write(st.session_state["feedback"])

if score_enabled:
    st.write(f"**Score:** {st.session_state.get('score',0)}")

# Knop voor nieuw woord (manueel)
if st.button("Nieuw woord"):
    nieuw_woord()
