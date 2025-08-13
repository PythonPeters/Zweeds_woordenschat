import streamlit as st
import pandas as pd
import random
import time

#versie10

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

# Titel
st.title("🇸🇪 Zweedse Woordenschat Trainer")

uploaded_file = st.file_uploader("Upload je woordenlijst (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)
    df.columns = ["Zweeds", "Nederlands"]

    # Richting kiezen
    richting = st.radio(
        "Kies richting",
        ["Zweeds → Nederlands", "Nederlands → Zweeds"]
    )

    # Init session state
    if "woord" not in st.session_state:
        st.session_state.woord = None
        st.session_state.juist = None
        st.session_state.score = 0
        st.session_state.resultaat = ""
        st.session_state.antwoord = ""

    # Nieuw woord functie (reset zonder scorewijziging!)
    def nieuw_woord():
        rij = df.sample().iloc[0]
        if richting == "Zweeds → Nederlands":
            st.session_state.woord = rij["Zweeds"]
            st.session_state.juist = rij["Nederlands"]
        else:
            st.session_state.woord = rij["Nederlands"]
            st.session_state.juist = rij["Zweeds"]
        st.session_state.resultaat = ""
        st.session_state.antwoord = ""

    # Eerste woord
    if st.session_state.woord is None:
        nieuw_woord()

    # Toon woord
    st.subheader(f"Vertaal: **{st.session_state.woord}**")

    # Antwoordveld
    antwoord = st.text_input("Jouw vertaling:", value=st.session_state.antwoord, key="antwoord")

    # Controleknop
    if st.button("Controleer"):
        if antwoord.strip():
            if antwoord.strip().lower() == st.session_state.juist.lower():
                st.session_state.resultaat = "✅ Juist!"
                st.session_state.score += 1
            else:
                st.session_state.resultaat = f"❌ Fout. Juist was: {st.session_state.juist}"
                st.session_state.score -= 1

    # Resultaat tonen
    if st.session_state.resultaat:
        st.write(st.session_state.resultaat)

    # Nieuw woord knop (nu zonder scorewijziging)
    if st.button("Nieuw woord"):
        nieuw_woord()

    # Score tonen
    st.write(f"**Score:** {st.session_state.score}")

else:
    st.info("⬆️ Upload een Excelbestand om te beginnen.")
