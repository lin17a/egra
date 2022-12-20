import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.plots import *
import time
import plost
import numpy as np


st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.header('Racing Simulador Dashboard')

# Row B
race_time_df = pd.read_csv("./stats_data/race_time.csv")
off_track_df = pd.read_csv("./stats_data/off_track.csv")
vel_n_time_df = pd.read_csv("./stats_data/vel_n_time.csv")
ia_data_df = pd.read_csv("./stats_data/Generations_1.csv")
# Col renaming
ia_cols = {'Unnamed: 0': 'i',
            '0': 'value'}
ia_data_df.rename(columns=ia_cols, inplace=True)

# Metrics
rescaling = lambda x : ((x / 30) * 100) * 3.725 # Formula f1-car spped
t = race_time_df["time"].values[0]
avg_vel = vel_n_time_df["velocity"].mean()
real_avg_vel = rescaling(avg_vel)
top_speedd = vel_n_time_df["velocity"].max()
real_top_speed = rescaling(top_speedd)

# Show metrics
col1, col2, col3 = st.columns(3)

col1.metric("Race finished in", f"{round(t, 2)} s", )
col2.metric("Average velocity", f"{round(real_avg_vel, 2)} KM/H") 
col3.metric("Top speed", f"{round(real_top_speed, 2)} KM/H") 

# Tabs
tab1, tab2 = st.tabs(["Race data", "AI data"])


with tab1:
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
                color = "#22181C")
    with c2:
        st.markdown('### Off track percentage')
        # Plot donut chart
        fig = donut_chart(off_track_df)
        st.plotly_chart(fig, use_container_width=True)
        #st.markdown('### Consistency')
        #prog_fig = progress_bar_chart(workout_consist)
        #st.plotly_chart(prog_fig)
with tab2:
    plost.line_chart(
        data=ia_data_df,
        x='i',
        y='value',
        width=1000,
        pan_zoom='both',
        color = "#22181C")  