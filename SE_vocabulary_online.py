import streamlit as st
import pandas as pd
import random

#
#versie10

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

st.title("🇸🇪 Ella's Zweedse Woordenschat Trainer")

uploaded_file = st.file_uploader("Upload je woordenlijst (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)
    df.columns = ["Zweeds", "Nederlands"]

    richting = st.radio(
        "Kies richting",
        ["Zweeds → Nederlands", "Nederlands → Zweeds"]
    )

    if "woord" not in st.session_state:
        st.session_state.woord = None
        st.session_state.juist = None
        st.session_state.score = 0
        st.session_state.resultaat = ""

    def nieuw_woord():
        rij = df.sample().iloc[0]
        if richting == "Zweeds → Nederlands":
            st.session_state.woord = rij["Zweeds"]
            st.session_state.juist = rij["Nederlands"]
        else:
            st.session_state.woord = rij["Nederlands"]
            st.session_state.juist = rij["Zweeds"]
        st.session_state.resultaat = ""

    if st.session_state.woord is None:
        nieuw_woord()

    st.subheader(f"Vertaal: **{st.session_state.woord}**")

    antwoord_input = st.text_input("Jouw vertaling:", value="", key=f"antwoord_{st.session_state.woord}")

    if st.button("Controleer"):
        if antwoord_input.strip():
            if antwoord_input.strip().lower() == st.session_state.juist.lower():
                st.session_state.resultaat = "✅ Juist!"
                st.session_state.score += 1
            else:
                st.session_state.resultaat = f"❌ Fout. Juist was: {st.session_state.juist}"
                st.session_state.score -= 1

    if st.session_state.resultaat:
        st.write(st.session_state.resultaat)

    if st.button("Nieuw woord"):
        nieuw_woord()

    st.write(f"**Score:** {st.session_state.score}")

else:
    st.info("⬆️ Upload een Excelbestand om te beginnen.")
