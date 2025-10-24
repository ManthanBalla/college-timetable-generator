import streamlit as st
import pandas as pd
import numpy as np
import os

# --------------------------------------------------------------
# ✅ PAGE CONFIG
# --------------------------------------------------------------
st.set_page_config(
    page_title="College Timetable Generator",
    page_icon="🧠",
    layout="wide"
)

# --------------------------------------------------------------
# 🎯 SIDEBAR MENU
# --------------------------------------------------------------
menu = st.sidebar.selectbox("📍 Navigate", ["Dashboard", "Generate Timetable", "About"])

# --------------------------------------------------------------
# 🧩 DASHBOARD SECTION
# --------------------------------------------------------------
if menu == "Dashboard":
    st.title("📊 Dashboard - College Timetable")

    st.write("Welcome to your college timetable generator dashboard!")

    # ✅ Google AdSense Integration
    st.markdown("""
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3249724202170570"
         crossorigin="anonymous"></script>
    <!-- Streamlit Dashboard Ad -->
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-3249724202170570"
         data-ad-slot="5516555758"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------
# 🧩 TIMETABLE GENERATOR SECTION
# --------------------------------------------------------------
elif menu == "Generate Timetable":
    st.title("🕒 Generate Timetable")
    st.write("Upload your timetable data and generate schedules without conflicts!")

# --------------------------------------------------------------
# 🧠 ABOUT SECTION
# --------------------------------------------------------------
elif menu == "About":
    st.title("ℹ️ About")
    st.write("This app generates optimized college timetables and now supports Google AdSense ads.")
