import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

st.title("🇸🇪 Ella's Zweedse Woordenschat Trainer")

# Upload Excelbestand
uploaded_file = st.file_uploader("📂 Kies je woordenlijst (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)
    df.columns = ["Zweeds", "Nederlands"]

    # Richting kiezen
    richting = st.radio(
        "Kies richting",
        ["Zweeds → Nederlands", "Nederlands → Zweeds"]
    )

    # Init sessiestate
    if "woord" not in st.session_state:
        st.session_state.woord = None
        st.session_state.juist = None
        st.session_state.resultaat = ""

    # Nieuw woord functie
    def nieuw_woord():
        rij = df.sample().iloc[0]
        if richting == "Zweeds → Nederlands":
            st.session_state.woord = rij["Zweeds"]
            st.session_state.juist = rij["Nederlands"]
        else:
            st.session_state.woord = rij["Nederlands"]
            st.session_state.juist = rij["Zweeds"]
        st.session_state.resultaat = ""  # reset melding

    # Eerste woord genereren
    if st.session_state.woord is None:
        nieuw_woord()

    st.subheader(f"Vertaal: **{st.session_state.woord}**")

    # Antwoordveld met Enter = controleren
    antwoord = st.text_input(
        "Jouw vertaling:",
        key="antwoordveld",
        on_change=lambda: controleer()
    )

    # Controlefunctie
    def controleer():
        if st.session_state.antwoordveld.strip().lower() == st.session_state.juist.lower():
            st.session_state.resultaat = "✅ Juist!"
        else:
            st.session_state.resultaat = f"❌ Fout. Juist was: {st.session_state.juist}"

    # Resultaat tonen
    if st.session_state.resultaat:
        st.write(st.session_state.resultaat)

    # Nieuw woord knop
    if st.button("Nieuw woord"):
        nieuw_woord()
        st.session_state.antwoordveld = ""  # veld leegmaken

else:
    st.info("⬆️ Upload een Excelbestand om te beginnen.")
