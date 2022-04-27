# Imports
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime


# Load in data
agg_df = pd.read_csv('.//Youtube_Dashboard//data//Aggregated_Metrics_By_Video.csv').iloc[1:, :]
sub_df = pd.read_csv('.//Youtube_Dashboard//data//Aggregated_Metrics_By_Country_And_Subscriber_status.csv')
comments_df = pd.read_csv('.//Youtube_Dashboard//data//All_Comments_Final.csv').iloc[1:, :]
performance_df = pd.read_csv('.//Youtube_Dashboard//data//Video_Performance_Over_Time.csv').iloc[1:, :]


# Testing
st.write(agg_df.head().to_string())
st.write(sub_df.head().to_string())
st.write(comments_df.head().to_string())
st.write(performance_df.head().to_string())