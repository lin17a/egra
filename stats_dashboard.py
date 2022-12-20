import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.plots import *
import time
import plost


st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.header('Racing Simulador Dashboard')

# Row B
race_time_df = pd.read_csv("./stats_data/race_time.csv")
t = race_time_df["time"].values[0]
off_track_df = pd.read_csv("./stats_data/off_track.csv")
vel_n_time_df = pd.read_csv("./stats_data/vel_n_time.csv")
v = 40

c1, c2 = st.columns((7,3)) # Columns

with c1:
    st.markdown('### Line chart showing average velocity across time')
    # PLot bar chart
    plost.line_chart(
            data=vel_n_time_df,
            x='time',
            y='velocity',
            width=1000,
            pan_zoom='both',
            color = "green")
    #st.plotly_chart(plot, use_container_width=True)
    c1.metric("Race finished in", f"{t} s") # TODO: Add increase/decrease
    c1.metric("Average velocity", f"{v} KM/H") # TODO: Add increase/decrease
with c2:
    st.markdown('### Off track percentage')
    # Plot donut chart
    fig = donut_chart(off_track_df)
    st.plotly_chart(fig, use_container_width=True)
#st.markdown('### Consistency')
#prog_fig = progress_bar_chart(workout_consist)
#st.plotly_chart(prog_fig)