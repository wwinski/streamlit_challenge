# Tutorial app from Day 9 of Streamlit 30 Days Challenge

# Imports
import streamlit as st
import pandas as pd
import numpy as np


# Page configs
st.set_page_config(page_title='Streamlit Day 9', page_icon=':sunglasses:', layout='centered')

# Streamlit Header
st.header('Examples: st.line_chart')

# Generate data
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['a', 'b', 'c'])

# Chart it
st.line_chart(chart_data)