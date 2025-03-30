import streamlit as st
import main_panel
import conviction_panel
import trade_log_panel
import performance_panel
import ml_panel

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Main Dashboard",
    "Conviction Score Panel",
    "Trade Log Panel",
    "Performance Panel",
    "ML Panel"
])

if page == "Main Dashboard":
    main_panel.run()
elif page == "Conviction Score Panel":
    conviction_panel.run()
elif page == "Trade Log Panel":
    trade_log_panel.run()
elif page == "Performance Panel":
    performance_panel.run()
elif page == "ML Panel":
    ml_panel.run()
