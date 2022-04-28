# Imports
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime
from pathlib import Path


# Global Functions

@st.cache  # This caches the function so we don't reload data every time the page loads
def load_data():
    '''
    Loads in the dataset from CSV files
    Applies some data manipulation (renaming, reformatting, etc..)
    Returns a tuple of dataframes
    '''

    # Read in the datasets
    agg_df = pd.read_csv(Path(__file__).parents[0] / 'data/Youtube_Dashboard/Aggregated_Metrics_By_Video.csv').iloc[1:, :]
    subscriber_df = pd.read_csv(Path(__file__).parents[0] / 'data/Youtube_Dashboard/Aggregated_Metrics_By_Country_And_Subscriber_status.csv')
    comments_df = pd.read_csv(Path(__file__).parents[0] / 'data/Youtube_Dashboard/All_Comments_Final.csv')
    performance_df = pd.read_csv(Path(__file__).parents[0] / 'data/Youtube_Dashboard/Video_Performance_Over_Time.csv')

    # Manipulations to datasets
    agg_df.columns = ['Video', 'Video title', 'Video publish time', 'Comments added', 'Shares', 'Dislikes', 'Likes', 'Subscribers lost',
                        'Subscribers gained', 'RPM(USD)', 'CPM(USD)', 'Average % viewed', 'Average view duration', 'Views',
                        'Watch time (hours)', 'Subscribers', 'Your estimated revenue (USD)', 'Impressions', 'Impressions ctr(%)']
    agg_df['Video publish time'] = pd.to_datetime(agg_df['Video publish time'])
    agg_df['Average view duration'] = agg_df['Average view duration'].apply(lambda val: datetime.strptime(val, '%H:%M:%S'))
    agg_df['Avg_duration_sec'] = agg_df['Average view duration'].apply(lambda val: val.second + val.minute * 60 + val.hour * 3600)
    agg_df['Engagement_ratio'] =  (agg_df['Comments added'] + agg_df['Shares'] + agg_df['Dislikes'] + agg_df['Likes']) / agg_df.Views
    agg_df['Views / sub gained'] = agg_df['Views'] / agg_df['Subscribers gained']
    agg_df.sort_values('Video publish time', ascending=False, inplace=True)
    performance_df['Date'] = pd.to_datetime(performance_df['Date'])

    (performance_diff, views_cumulative) = get_daily_data(agg_df, performance_df)

    return (agg_df, subscriber_df, comments_df, performance_df, get_agg_diff(agg_df), performance_diff, views_cumulative)


def get_agg_diff(agg_df):
    # Get median values from past 12 months
    diff_df = agg_df.copy()
    metric_date_12mo = diff_df['Video publish time'].max() - pd.DateOffset(months=12)
    median_agg = diff_df[diff_df['Video publish time'] >= metric_date_12mo].median()

    # Get differenced values from the median
    numeric_cols = np.array((diff_df.dtypes == 'float64') | (diff_df.dtypes == 'int64'))
    diff_df.iloc[:,numeric_cols] = (diff_df.iloc[:,numeric_cols] - median_agg).div(median_agg)
    diff_df['Publish_date'] = diff_df['Video publish time'].apply(lambda val: val.date())  # Format to string date

    return diff_df


def get_daily_data(agg_df, performance_df):
    #merge daily data with publish data to get delta 
    performance_diff = pd.merge(performance_df, agg_df.loc[:, ['Video','Video publish time']], left_on='External Video ID', right_on='Video')
    performance_diff['days_published'] = (performance_diff['Date'] - performance_diff['Video publish time']).dt.days

    # get last 12 months of data rather than all data 
    date_12mo = agg_df['Video publish time'].max() - pd.DateOffset(months=12)
    performance_diff_year = performance_diff[performance_diff['Video publish time'] >= date_12mo]

    # get daily view data (first 30), median & percentiles 
    agg_funcs = [np.mean, np.median, lambda x: np.percentile(x, 80), lambda x: np.percentile(x, 20)]
    views_days = pd.pivot_table(performance_diff_year, index='days_published', values='Views', aggfunc=agg_funcs).reset_index()
    views_days.columns = ['days_published', 'mean_views', 'median_views', '80pct_views', '20pct_views']
    views_days = views_days[views_days['days_published'].between(0,30)]
    views_cumulative = views_days.loc[:, ['days_published', 'median_views', '80pct_views', '20pct_views']] 
    views_cumulative.loc[:, ['median_views', '80pct_views', '20pct_views']] = views_cumulative.loc[:, ['median_views', '80pct_views', '20pct_views']].cumsum()

    return (performance_diff, views_cumulative)



def write_aggregate_metrics(agg_df, diff_df):
    '''
    Writes aggregate video metrics to streamlit.
    Creates overall metrics values as well as an interactive dataframe.
    '''
    
    # Get median comparison from 6mo vs 12mo lookback
    agg_cols = ['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed','Avg_duration_sec', 'Engagement_ratio','Views / sub gained']
    df_agg_metrics = agg_df[agg_cols].copy()
    metric_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months=6)
    metric_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months=12)
    metric_medians_6mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_6mo].median()
    metric_medians_12mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_12mo].median()

    # For each metric (column) write the value and the delta between the medians per lookback
    streamlit_cols = st.columns(5)
    for i, col_name in enumerate(metric_medians_6mo.index):
        streamlit_column = streamlit_cols[i % 5]  # After 5 metrics, skip to new "row"
        delta = (metric_medians_6mo[col_name] - metric_medians_12mo[col_name]) / metric_medians_12mo[col_name]
        streamlit_column.metric(label=col_name, value=round(metric_medians_6mo[col_name], 1), delta="{:.2%}".format(delta))


    # Write the data to a visual df
    agg_cols = ['Video title','Publish_date','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed','Avg_duration_sec', 'Engagement_ratio','Views / sub gained']
    final_df = diff_df.loc[:, agg_cols]  # Keep only the columns we care about
    
    # For each column set the format
    df_to_pct = {}
    for col_name in final_df.median().index.tolist():
        df_to_pct[col_name] = '{:.1%}'.format
    
    # Write the dataframe to Streamlit
    st.dataframe(final_df.style.hide().applymap(style_df_vals).format(df_to_pct))


def write_individual_video_metrics(agg_df, subscriber_df, performance_diff, views_cumulative):
    ''' Will be used to create/format/write metrics for individual video performance '''
    
    # Populate list of videos and get selected
    videos = tuple(agg_df['Video title'])
    selected_video = st.selectbox('Pick a Video:', videos)
    
    # Columns to hold charts
    col1, col2 = st.columns(2)

    # Filter data to selected video
    sub_filtered = subscriber_df[subscriber_df['Video Title'] == selected_video].copy()
    sub_filtered['Country'] = sub_filtered['Country Code'].apply(country_code_map)
    sub_filtered.sort_values('Is Subscribed', inplace= True)   
    
    # Create chart for filtered data
    fig = px.bar(sub_filtered, x='Views', y='Is Subscribed', color='Country', orientation='h')
    col1.plotly_chart(fig)
    
    # Get data during the first 30 days
    agg_time_filtered = performance_diff[performance_diff['Video Title'] == selected_video].copy()
    first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0,30)]
    first_30 = first_30.sort_values('days_published')

    # Chart metrics for first 30 days (video aggregates vs this video)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['20pct_views'],
                    mode='lines', name='20th percentile', line=dict(color='purple', dash ='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['median_views'],
                        mode='lines', name='50th percentile', line=dict(color='black', dash ='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['80pct_views'],
                        mode='lines', name='80th percentile', line=dict(color='royalblue', dash ='dash')))
    fig2.add_trace(go.Scatter(x=first_30['days_published'], y=first_30['Views'].cumsum(),
                        mode='lines', name='Current Video' ,line=dict(color='firebrick',width=8)))
    fig2.update_layout(title='View comparison first 30 days', xaxis_title='Days Since Published', yaxis_title='Cumulative views')
    col2.plotly_chart(fig2)


def style_df_vals(v):
    ''' Used to color the numeric values in streamlit dataframe '''
    # Adding try/except to account for timestamp columns - pretty hacky
    try: 
        if v < 0:  # Negative values
            return 'color:red;'
        elif v > 0:  # Positive Values
            return 'color:green;'
        else:
            return None
    except:
        pass


def country_code_map(country_code):
    # Only supporting USA and India for now (majority of data)
    if country_code == 'US':
        return 'USA'
    if country_code == 'IN':
        return 'India'
    return 'Other'



##### Main #####

# Use the full page instead of a narrow central column
st.set_page_config(page_title='Ken Jee YouTube Data', page_icon=':chart_with_upwards_trend:', layout="wide")

import os
st.header(os.listdir(Path(__file__).parents[0] / 'data/Youtube_Dashboard/'))
exit()

# Read in data
(agg_df, subscriber_df, comments_df, performance_df, diff_df, performance_diff, views_cumulative) = load_data()

# Show separate dashboard based on selection
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics','Individual Video Analysis'))
if add_sidebar == 'Aggregate Metrics':
    st.header('Ken Jee YouTube Aggregated Data')
    write_aggregate_metrics(agg_df, diff_df)
elif add_sidebar == 'Individual Video Analysis':
    st.header('Ken Jee YouTube Individual Video Metrics')
    write_individual_video_metrics(agg_df, subscriber_df, performance_diff, views_cumulative)