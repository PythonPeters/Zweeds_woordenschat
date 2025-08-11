import streamlit as st
import pandas as pd
import time
import requests
from io import BytesIO

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

# === Instellingen ===
dropbox_url = "https://www.dropbox.com/scl/fi/4gs3ccprk97a5qjtefmk9/woorden-All.xlsx?rlkey=p4wrbilpb8v5cyb8uzq9i9um7&st=8rs9gc87&dl=1"  # <-- Pas dit aan

# === Woordenlijst laden ===
try:
    response = requests.get(dropbox_url)
    response.raise_for_status()
    df = pd.read_excel(BytesIO(response.content), header=None, engine="openpyxl")
    df.columns = ["Zweeds", "Nederlands"]
except Exception as e:
    st.error(f"Fout bij het laden van de woordenlijst: {e}")
    st.stop()

# === Titel ===
st.title("🇸🇪 Ella's Zweedse Woordenschat Trainer")

# Richting kiezen
richting = st.radio(
    "Kies richting",
    ["Zweeds → Nederlands", "Nederlands → Zweeds"]
)

# Opties
col1, col2 = st.columns(2)
with col1:
    score_enabled = st.checkbox("Score bijhouden", value=False)
with col2:
    timer_enabled = st.checkbox("Timer gebruiken", value=False)

# Timer-instelling
timer_secs = 10
if timer_enabled:
    timer_secs = st.number_input("Aantal seconden per woord", min_value=3, max_value=60, value=10)

# Sessiestate initialiseren
if "woord" not in st.session_state:
    st.session_state.woord = None
    st.session_state.juist = None
    st.session_state.score = 0
    st.session_state.start_time = None
    st.session_state.tijd_op = False
    st.session_state.resultaat = ""
    st.session_state.antwoord = ""
    st.session_state.auto_nieuw = False  # Nieuw vlaggetje

# Nieuw woord functie
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
    st.session_state.resultaat = ""
    st.session_state.auto_nieuw = False

# Controle functie
def controleer():
    if not st.session_state.tijd_op:
        if st.session_state.antwoord.strip().lower() == st.session_state.juist.lower():
            st.session_state.resultaat = "✅ Juist!"
            if score_enabled:
                st.session_state.score += 1
            st.session_state.auto_nieuw = True  # Zet vlag aan
        else:
            st.session_state.resultaat = f"❌ Fout. Juist was: {st.session_state.juist}"
            if score_enabled:
                st.session_state.score -= 1

# Automatisch nieuw woord na juist antwoord
if st.session_state.auto_nieuw:
    time.sleep(1)
    nieuw_woord()

# Knop voor nieuw woord
if st.button("Nieuw woord"):
    nieuw_woord()

# Woord tonen
if st.session_state.woord:
    st.subheader(f"Vertaal: **{st.session_state.woord}**")

    # Timer
    if timer_enabled and st.session_state.start_time:
        resterend = timer_secs - int(time.time() - st.session_state.start_time)
        if resterend > 0:
            st.info(f"⏳ Tijd: {resterend} sec")
        else:
            if not st.session_state.tijd_op:
                st.session_state.resultaat = f"⏰ Tijd voorbij! Juist was: **{st.session_state.juist}**"
                if score_enabled:
                    st.session_state.score -= 1
                st.session_state.tijd_op = True

    # Antwoordveld (Enter triggert controle)
    st.text_input(
        "Jouw vertaling:",
        value=st.session_state.antwoord,
        key="antwoord",
        on_change=controleer
    )

    # Resultaat tonen
    if st.session_state.resultaat:
        if "✅" in st.session_state.resultaat:
            st.success(st.session_state.resultaat)
        elif "❌" in st.session_state.resultaat:
            st.error(st.session_state.resultaat)
        else:
            st.warning(st.session_state.resultaat)

    # Score tonen
    if score_enabled:
        st.write(f"**Score:** {st.session_state.score}")
