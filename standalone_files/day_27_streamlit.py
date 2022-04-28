# Tutorial app from Day 27 of Streamlit 30 Days Challenge

# Imports
import json
import streamlit as st
from pathlib import Path
from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo

# Page configs
st.set_page_config(page_title='Streamlit Day 19', page_icon=':sunglasses:', layout='wide')


# Sidebar Data and Input
with st.sidebar:
    st.title("🗓️ #30DaysOfStreamlit")
    st.header("Day 27 - Streamlit Elements")
    st.write("Build a draggable and resizable dashboard with Streamlit Elements.")
    st.write("---")

    # Define URL for media player.
    media_url = st.text_input("Media URL", value="https://www.youtube.com/watch?v=Yk-unX4KnV4&ab_channel=KenJee")


# Initialize default data for code editor and chart.
#
# For this tutorial, we will need data for a Nivo Bump chart.
# You can get random data there, in tab 'data': https://nivo.rocks/bump/
#
# As you will see below, this session state item will be updated when our
# code editor change, and it will be read by Nivo Bump chart to draw the data.

if "data" not in st.session_state:
    st.session_state.data = Path("data/bump_data.json").read_text()

# Define a default dashboard layout
# Dashboard grid has 12 columns by default
layout = [
    # Editor item is positioned in coordinates x=0 and y=0, and takes 6/12 columns and has a height of 3.
    dashboard.Item("editor", 0, 0, 6, 3),
    # Chart item is positioned in coordinates x=6 and y=0, and takes 6/12 columns and has a height of 3.
    dashboard.Item("chart", 6, 0, 6, 3),
    # Media item is positioned in coordinates x=0 and y=3, and takes 6/12 columns and has a height of 4.
    dashboard.Item("media", 0, 2, 12, 4),
]

# Create a frame to display elements.
with elements("demo"):

    # Create a new dashboard with the layout specified above
    with dashboard.Grid(layout, draggableHandle=".draggable"):
        # First card, the code editor.
        with mui.Card(key="editor", sx={"display": "flex", "flexDirection": "column"}):
            mui.CardHeader(title="Editor", className="draggable")
            # We want to make card's content take all the height available by setting flex CSS value to 1.
            # We also want card's content to shrink when the card is shrinked by setting minHeight to 0.
            with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
                editor.Monaco(
                    defaultValue=st.session_state.data,
                    language="json",
                    onChange=lazy(sync("data"))
                )

            with mui.CardActions:
                # Monaco editor has a lazy callback bound to onChange, which means that even if you change
                # Monaco's content, Streamlit won't be notified directly, thus won't reload everytime.
                # So we need another non-lazy event to trigger an update.
                # The solution is to create a button that fires a callback on click.
                mui.Button("Apply changes", onClick=sync())

        # Second card, the Nivo Bump chart.
        with mui.Card(key="chart", sx={"display": "flex", "flexDirection": "column"}):
            mui.CardHeader(title="Chart", className="draggable")
            with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
                nivo.Bump(
                    data=json.loads(st.session_state.data),
                    colors={ "scheme": "spectral" },
                    lineWidth=3,
                    activeLineWidth=6,
                    inactiveLineWidth=3,
                    inactiveOpacity=0.15,
                    pointSize=10,
                    activePointSize=16,
                    inactivePointSize=0,
                    pointColor={ "theme": "background" },
                    pointBorderWidth=3,
                    activePointBorderWidth=3,
                    pointBorderColor={ "from": "serie.color" },
                    axisTop={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legend": "",
                        "legendPosition": "middle",
                        "legendOffset": -36
                    },
                    axisBottom={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legend": "",
                        "legendPosition": "middle",
                        "legendOffset": 32
                    },
                    axisLeft={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legend": "ranking",
                        "legendPosition": "middle",
                        "legendOffset": -40
                    },
                    margin={ "top": 40, "right": 100, "bottom": 40, "left": 60 },
                    axisRight=None,
                )

        # Third element of the dashboard, the Media player.
        with mui.Card(key="media", sx={"display": "flex", "flexDirection": "column"}):
            mui.CardHeader(title="Media Player", className="draggable")
            with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
                # This element is powered by ReactPlayer
                media.Player(url=media_url, width="100%", height="100%", controls=True)