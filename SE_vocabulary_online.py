import streamlit as st
import pandas as pd
import random
import time
import requests
from io import BytesIO

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

# Titel
st.title("🇸🇪 Zweedse Woordenschat Trainer")

# Dropbox link invoer
dropbox_link = st.text_input("Plak hier de Dropbox-link naar je woordenlijst (Excel)")

if dropbox_link:
    try:
        # Link aanpassen zodat deze direct downloadt
        if "?dl=0" in dropbox_link:
            dropbox_link = dropbox_link.replace("?dl=0", "?dl=1")

        # Excel downloaden vanuit Dropbox
        response = requests.get(dropbox_link)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), header=None)
        df.columns = ["Zweeds", "Nederlands"]

        # Richting kiezen
        richting = st.radio("Kies richting", ["Zweeds → Nederlands", "Nederlands → Zweeds"])

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

        # Sessiestate
        if "woord" not in st.session_state:
            st.session_state.woord = None
            st.session_state.juist = None
            st.session_state.score = 0
            st.session_state.start_time = None
            st.session_state.tijd_op = False
            st.session_state.antwoord = ""

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

        # Nieuw woord knop
        if st.button("Nieuw woord"):
            nieuw_woord()

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

            # Antwoordveld met Enter-detectie
            antwoord = st.text_input("Jouw vertaling:", value=st.session_state.antwoord, key="antwoord")
            if st.button("Controleer") or (antwoord and antwoord.endswith("\n")):
                if not st.session_state.tijd_op:
                    if antwoord.strip().lower() == st.session_state.juist.lower():
                        st.success("✅ Juist!")
                        if score_enabled:
                            st.session_state.score += 1
                    else:
                        st.error(f"❌ Fout. Juist was: {st.session_state.juist}")
                        if score_enabled:
                            st.session_state.score -= 1

            # Score tonen
            if score_enabled:
                st.write(f"**Score:** {st.session_state.score}")

    except Exception as e:
        st.error(f"Fout bij het laden van de woordenlijst: {e}")

else:
    st.info("📥 Plak hierboven je Dropbox-link om te beginnen.")
