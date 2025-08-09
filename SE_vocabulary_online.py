import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

# Titel
st.title("🇸🇪 Zweeds Woordenschat Trainer")

# Upload Excelbestand
uploaded_file = st.file_uploader("Upload je woordenlijst (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)
    df.columns = ["Zweeds", "Nederlands"]

    # Richting kiezen
    richting = st.radio(
        "Kies richting",
        ["Zweeds → Nederlands", "Nederlands → Zweeds"]
    )

    # Opties
    col1, col2 = st.columns(2)
    with col1:
        score_enabled = st.checkbox("Score bijhouden", value=True)
    with col2:
        timer_enabled = st.checkbox("Timer gebruiken", value=True)

    # Timer-instelling
    timer_secs = 10
    if timer_enabled:
        timer_secs = st.number_input("Aantal seconden per woord", min_value=3, max_value=60, value=10)

    # Sessiestate
    if "woord" not in st.session_state:
        st.session_state.woord = None
        st.session_state.juist = None
        st.session_state.score = 0
        st.session_state.start_time = None
        st.session_state.tijd_op = False

    # Nieuw woord
    if st.button("Nieuw woord"):
        rij = df.sample().iloc[0]
        if richting == "Zweeds → Nederlands":
            st.session_state.woord = rij["Zweeds"]
            st.session_state.juist = rij["Nederlands"]
        else:
            st.session_state.woord = rij["Nederlands"]
            st.session_state.juist = rij["Zweeds"]
        st.session_state.start_time = time.time()
        st.session_state.tijd_op = False

    # Woord tonen
    if st.session_state.woord:
        st.subheader(f"Vertaal: **{st.session_state.woord}**")

        # Timer
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

        # Antwoordveld
        antwoord = st.text_input("Jouw vertaling:")

        # Controle
        if st.button("Controleer"):
            if not st.session_state.tijd_op:
                if antwoord.strip().lower() == st.session_state.juist.lower():
                    st.success("✅ Juist!")
                    if score_enabled:
                        st.session_state.score += 1
                else:
                    st.error(f"❌ Fout. Juist was: {st.session_state.juist}")
                    if score_enabled:
                        st.session_state.score -= 1

        # Score
        if score_enabled:
            st.write(f"**Score:** {st.session_state.score}")

else:
    st.info("⬆️ Upload een Excelbestand om te beginnen.")
