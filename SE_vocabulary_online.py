import streamlit as st
import pandas as pd
import time

#versie12 - defintief

st.set_page_config(page_title="Zweeds Trainer", page_icon="🇸🇪")

st.title("🇸🇪 Zweedse Woordenschat Trainer")

# Upload Excelbestand
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

    col1, col2, col3 = st.columns(3)
    with col1:
        score_enabled = st.checkbox("Score bijhouden", value=True)
    with col2:
        timer_enabled = st.checkbox("Timer gebruiken", value=True)
    with col3:
        if st.button("🔄 Reset score"):
            st.session_state.score = 0
            st.session_state.aantal_ingaves = 0
            st.session_state.resultaat = ""
            st.session_state.antwoord_verwerkt = False
            st.session_state.auto_next = False
            st.session_state.performed_reload = False
            st.session_state.is_new_word = False

    timer_secs = 10
    if timer_enabled:
        timer_secs = st.number_input("Aantal seconden per woord", min_value=3, max_value=60, value=10)

    # Sessiestate
    if "woord" not in st.session_state:
        st.session_state.woord = None
        st.session_state.juist = None
        st.session_state.score = 0
        st.session_state.aantal_ingaves = 0
        st.session_state.start_time = None
        st.session_state.tijd_op = False
        st.session_state.resultaat = ""
        st.session_state.antwoord = ""
        st.session_state.auto_next = False
        st.session_state.performed_reload = False
        st.session_state.is_new_word = False
        st.session_state.antwoord_verwerkt = False

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
        st.session_state.is_new_word = True
        st.session_state.antwoord_verwerkt = False

    def controleer():
        if st.session_state.antwoord_verwerkt:
            return

        if st.session_state.is_new_word and st.session_state.antwoord.strip() == "":
            st.session_state.is_new_word = False
            return

        st.session_state.is_new_word = False
        st.session_state.antwoord_verwerkt = True

        # Tel altijd een ingave
        st.session_state.aantal_ingaves += 1

        if not st.session_state.tijd_op:
            antwoord = st.session_state.antwoord.strip().lower()
            juist = st.session_state.juist.strip().lower()
            if antwoord != "" and antwoord == juist:
                st.session_state.resultaat = "✅ Juist!"
                if score_enabled:
                    st.session_state.score += 1
                st.session_state.auto_next = True
                st.session_state.next_delay = 1
                st.session_state.performed_reload = False
            elif antwoord != "":
                st.session_state.resultaat = f"❌ Fout. Juist was: {st.session_state.juist}"
                if score_enabled:
                    st.session_state.score -= 1
                st.session_state.auto_next = True
                st.session_state.next_delay = 2
                st.session_state.performed_reload = False

    if st.button("Nieuw woord"):
        nieuw_woord()

    if st.session_state.auto_next:
        if not st.session_state.performed_reload:
            st.session_state.performed_reload = True
            time.sleep(st.session_state.get("next_delay", 1))
            nieuw_woord()

    if st.session_state.woord is None:
        nieuw_woord()

    if st.session_state.woord:
        st.subheader(f"Vertaal: **{st.session_state.woord}**")

        if timer_enabled and st.session_state.start_time:
            elapsed = int(time.time() - st.session_state.start_time)
            resterend = timer_secs - elapsed
            if resterend > 0:
                st.info(f"⏳ Tijd: {resterend} sec")
            else:
                if not st.session_state.tijd_op:
                    st.session_state.resultaat = f"⏰ Tijd voorbij! Juist was: {st.session_state.juist}"
                    if score_enabled:
                        st.session_state.score -= 1
                    st.session_state.tijd_op = True

        with st.form(key="antwoord_form", clear_on_submit=False):
            st.text_input(
                "Jouw vertaling:",
                value=st.session_state.antwoord,
                key="antwoord"
            )
            submit_button = st.form_submit_button("Controleer")
            if submit_button:
                controleer()

        if st.session_state.resultaat:
            if st.session_state.resultaat.startswith("✅"):
                st.success(st.session_state.resultaat)
            elif st.session_state.resultaat.startswith("❌"):
                st.error(st.session_state.resultaat)
            else:
                st.warning(st.session_state.resultaat)

        if score_enabled:
            st.write(f"**Score:** {st.session_state.score}")

        if st.session_state.aantal_ingaves > 0:
            percentage = (st.session_state.score / st.session_state.aantal_ingaves) * 100
            st.write(f"**Aantal ingaves:** {st.session_state.aantal_ingaves}")
            st.write(f"**Percentage correct:** {percentage:.1f}%")

else:
    st.info("⬆️ Upload een Excelbestand om te beginnen.")
