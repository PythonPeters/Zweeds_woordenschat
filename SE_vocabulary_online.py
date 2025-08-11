import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

st.title("🇸🇪 Ella's Zweedse Woordenschat Trainer")

uploaded_file = st.file_uploader("Upload je woordenlijst (Excel)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None, engine="openpyxl")
        df.columns = ["Zweeds", "Nederlands"]
    except Exception as e:
        st.error(f"Fout bij het laden van de woordenlijst: {e}")
        st.stop()

    richting = st.radio(
        "Kies richting",
        ["Zweeds → Nederlands", "Nederlands → Zweeds"]
    )

    # Sessiestate
    if "woord" not in st.session_state:
        st.session_state.woord = None
        st.session_state.juist = None
        st.session_state.resultaat = ""
        st.session_state.antwoord = ""
        st.session_state.wachten_op_volgend = False

    def nieuw_woord():
        rij = df.sample().iloc[0]
        if richting == "Zweeds → Nederlands":
            st.session_state.woord = rij["Zweeds"]
            st.session_state.juist = rij["Nederlands"]
        else:
            st.session_state.woord = rij["Nederlands"]
            st.session_state.juist = rij["Zweeds"]
        st.session_state.antwoord = ""
        st.session_state.resultaat = ""
        st.session_state.wachten_op_volgend = False

    def controleer():
        antwoord = st.session_state.antwoord.strip().lower()
        juist = st.session_state.juist.strip().lower()
        if antwoord == juist:
            st.session_state.resultaat = "✅ Juist!"
            nieuw_woord()
        else:
            st.session_state.resultaat = f"❌ Fout. Juist was: {st.session_state.juist}"
            st.session_state.wachten_op_volgend = True

    # Knop voor handmatig nieuw woord
    if st.button("Nieuw woord"):
        nieuw_woord()

    # Eerste keer woord laden
    if st.session_state.woord is None:
        nieuw_woord()

    # Woord tonen
    st.subheader(f"Vertaal: **{st.session_state.woord}**")

    # Antwoordveld
    st.text_input(
        "Jouw vertaling:",
        key="antwoord",
        on_change=controleer
    )

    # Resultaat tonen
    if st.session_state.resultaat:
        if st.session_state.resultaat.startswith("✅"):
            st.success(st.session_state.resultaat)
        else:
            st.error(st.session_state.resultaat)
            # Automatisch nieuw woord na 2,5 sec bij fout antwoord
            if st.session_state.wachten_op_volgend:
                time.sleep(2.5)
                nieuw_woord()
                st.experimental_rerun()

else:
    st.info("⬆️ Upload een Excelbestand om te beginnen.")
