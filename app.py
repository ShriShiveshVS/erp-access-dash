import streamlit as st
import pandas as pd
from ui_renderer import render_ui

st.set_page_config(page_title="ERP Role Access Intelligence", layout="wide")
st.title("🛡️ ERP Role Access Intelligence Dashboard")

col1, col2 = st.columns(2)
with col1:
    hr_file = st.file_uploader("Upload HR Master File", type=["xlsx"])
with col2:
    access_file = st.file_uploader("Upload Access Data File", type=["xlsx"])

if hr_file and access_file:
    hr_df = pd.read_excel(hr_file)
    access_df = pd.read_excel(access_file)
    render_ui(hr_df, access_df)
else:
    st.warning("⬆️ Please upload both files to continue.")
