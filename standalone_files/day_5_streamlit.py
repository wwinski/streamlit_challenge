# Tutorial app from Day 5 of Streamlit 30 Days Challenge

# Imports
import numpy as np
import altair as alt
import pandas as pd
import streamlit as st


# Page configs
st.set_page_config(page_title='Streamlit Day 5', page_icon=':sunglasses:', layout='centered')

# Streamlit Header
st.header('Examples: st.write')

# Example 1 - Italics and emoji
st.write('Hello, *World!* :sunglasses:')

# Example 2 - Numeric (shows kind of like a code/quote block)
st.write(1234)

# Example 3 -  Dataframe table
df = pd.DataFrame(
     {
          'first column': [1, 2, 3, 4],
          'second column': [10, 20, 30, 40]
     }
)
st.write(df)

# Example 4 - Multiple arguments
st.write('Below is a DataFrame:', df, 'Above is a dataframe.')

# Example 5 - Charting from a df
df2 = pd.DataFrame(np.random.randn(200, 3), columns=['a', 'b', 'c'])
c = alt.Chart(df2).mark_circle().encode(x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
st.write(c)
