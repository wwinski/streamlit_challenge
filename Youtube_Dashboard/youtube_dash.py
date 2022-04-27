# Imports
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as pval
import streamlit as st
from datetime import datetime


# Global Functions

@st.cache  # This caches the function so we don't reload data every time the page loads
def load_data():
    '''
    Loads in the dataset from CSV files
    Applies some data manipulation (renaming, reformatting, etc..)
    Returns a tuple of dataframes
    '''

    # Read in the datasets
    agg_df = pd.read_csv('.//Youtube_Dashboard//data//Aggregated_Metrics_By_Video.csv').iloc[1:, :]
    subscriber_df = pd.read_csv('.//Youtube_Dashboard//data//Aggregated_Metrics_By_Country_And_Subscriber_status.csv')
    comments_df = pd.read_csv('.//Youtube_Dashboard//data//All_Comments_Final.csv').iloc[1:, :]
    performance_df = pd.read_csv('.//Youtube_Dashboard//data//Video_Performance_Over_Time.csv').iloc[1:, :]

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

    return (agg_df, subscriber_df, comments_df, performance_df, get_agg_diff(agg_df))


def get_agg_diff(agg_df):
    # Get median values from past 12 months
    diff_df = agg_df.copy()
    metric_date_12mo = diff_df['Video publish time'].max() - pd.DateOffset(months=12)
    median_agg = diff_df[diff_df['Video publish time'] >= metric_date_12mo].median()

    # Get differenced values from the median
    numeric_cols = np.array((diff_df.dtypes == 'float64') | (diff_df.dtypes == 'int64'))
    diff_df.iloc[:,numeric_cols] = (diff_df.iloc[:,numeric_cols] - median_agg).div(median_agg)

    return diff_df


def write_aggregate_metrics(agg_df, diff_df):
    '''
    Writes aggregate video metrics to streamlit.
    Creates overall metrics values as well as an interactive dataframe.
    '''
    
    # Get median comparison from 6mo vs 12mo lookback
    agg_cols = ['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed','Avg_duration_sec', 'Engagement_ratio','Views / sub gained']
    df_agg_metrics = agg_df[agg_cols]
    metric_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months =6)
    metric_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months =12)
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
    diff_df['Publish_date'] = diff_df['Video publish time'].apply(lambda val: val.date())  # Format to string date
    final_df = diff_df.loc[:, agg_cols]  # Keep only the columns we care about
    
    # For each column set the format
    df_to_pct = {}
    for col_name in final_df.median().index.tolist():
        df_to_pct[col_name] = '{:.1%}'.format
    
    # Write the dataframe to Streamlit
    st.dataframe(final_df.style.hide().applymap(style_df_vals).format(df_to_pct))


def write_individual_video_metrics():
    ''' Will be used to create/format/write metrics for individual video performance '''
    pass

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


# Main
(agg_df, subscriber_df, comments_df, performance_df, diff_df) = load_data()


add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics','Individual Video Analysis'))
if add_sidebar == 'Aggregate Metrics':
    st.write('Ken Jee YouTube Aggregated Data')
    write_aggregate_metrics(agg_df, diff_df)
elif add_sidebar == 'Individual Video Analysis':
    st.write('Ken Jee YouTube Individual Video Metrics')
    write_individual_video_metrics()