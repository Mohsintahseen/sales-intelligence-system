"""Sales Intelligence: Streamlit app entry point.

All data is SIMULATED (Maven Analytics Global Electronics Retailer dataset).

Run from the project root:
    streamlit run app/streamlit_app.py
"""
import streamlit as st

st.set_page_config(page_title="Sales Intelligence", layout="wide")

pages = [
    st.Page("overview.py", title="Overview", default=True),
    st.Page("forecast.py", title="Forecast"),
]
st.navigation(pages).run()
