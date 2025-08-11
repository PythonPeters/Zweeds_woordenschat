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

    col1, col2 = st.columns(2)
    with col1:
        score_enabled = st.checkbox("Score bijhouden", value=False)
    with col2:
        timer_enabled = st.checkbox("Timer gebruiken", value=False)

    timer_secs = 10
    if timer_enabled:
        timer_secs = st.number_input("Aantal seconden per woord", min_value=3, max_value=60, value=10)

    if "woord" not in st.session_state:
        st.session_state.woord = None
        st.session_state.juist = None
        st.session_state.score = 0
        st.session_state.start_time = None
        st.session_state.tijd_op = False
        st.session_state.resultaat = ""
        st.session_state.antwoord = ""
        st.session_state.auto_next = False
        st.session_state.performed_reload = False

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
        st.session_state.auto_next = False
        st.session_state.performed_reload = False

    def controleer():
        if not st.session_state.tijd_op:
            antwoord = st.session_state.get("antwoord", "").strip().lower()
            juist = st.session_state.get("juist", "").strip().lower()
            if antwoord != "" and antwoord == juist:
                st.session_state.resultaat = "✅ Juist!"
                if score_enabled:
                    st.session_state.score += 1
                st.session_state.auto_next = True
                st.session_state.performed_reload = False
            else:
                st.session_state.resultaat = f"❌ Fout. Juist was: {st.session_state.get('juist','')}"
                if score_enabled:
                    st.session_state.score -= 1

    # Nieuw woord knop zonder score wijziging
    if st.button("Nieuw woord"):
        nieuw_woord()

    # Automatisch nieuw woord na correct antwoord
    if st.session_state.auto_next:
        if not st.session_state.performed_reload:
            st.session_state.performed_reload = True
            js = "<script>setTimeout(()=>location.reload(), 1000);</script>"
            st.markdown(js, unsafe_allow_html=True)
        else:
            nieuw_woord()

    if st.session_state.woord:
        st.subheader(f"Vertaal: **{st.session_state.woord}**")

        if timer_enabled and st.session_state.start_time:
            resterend = timer_secs - int(time.time() - st.session_state.start_time)
            if resterend > 0:
                st.info(f"⏳ Tijd: {resterend} sec")
            else:
                if not st.session_state.tijd_op:
                    st.session_state.resultaat = f"⏰ Tijd voorbij! Juist was: {st.session_state.juist}"
                    if score_enabled:
                        st.session_state.score -= 1
                    st.session_state.tijd_op = True

        st.text_input(
            "Jouw vertaling:",
            value=st.session_state.antwoord,
            key="antwoord",
            on_change=controleer
        )

        if st.session_state.resultaat:
            if st.session_state.resultaat.startswith("✅"):
                st.success(st.session_state.resultaat)
            elif st.session_state.resultaat.startswith("❌"):
                st.error(st.session_state.resultaat)
            else:
                st.warning(st.session_state.resultaat)

        if score_enabled:
            st.write(f"**Score:** {st.session_state.score}")

else:
    st.info("⬆️ Upload een Excelbestand om te beginnen.")
