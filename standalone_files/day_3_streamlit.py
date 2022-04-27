# Tutorial app from Day 3 of Streamlit 30 Days Challenge

# Imports
import streamlit as st


# Streamlit Header
st.header('st.button')

# Streamlit Button with variable output
if st.button('Say hello'):
     st.write('Why hello there')
else:
     st.write('Goodbye')