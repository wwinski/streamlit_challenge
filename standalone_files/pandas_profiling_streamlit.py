# Tutorial app from Day 14 of Streamlit 30 Days Challenge

# Imports
import streamlit as st
import pandas as pd
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report

# Streamlit Header
st.header('`streamlit_pandas_profiling`')

# Read data from web
df = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/penguins_cleaned.csv')

# Create profile and write to streamlit
pr = df.profile_report()
st_profile_report(pr)