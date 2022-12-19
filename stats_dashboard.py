import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.plots import *
import time


st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.header('Racing Simulador Dashboard')

# Row B
race_time_df = pd.read_csv("./stats_data/race_time.csv")
off_track_df = pd.read_csv("./stats_data/off_track.csv")
avg_car1_vel_df = pd.read_csv("./stats_data/avg_car_vel.csv")

c1, c2 = st.columns((7,3)) # Columns


with c1:
    st.markdown('### Line chart showing average velocity across time')
    # PLot bar chart
    plot = bar_chart(avg_car1_vel_df)
    st.plotly_chart(plot, use_container_width=True)
    st.write(f'\nRace finished in **{race_time_df["time"].values[0]} s**')
with c2:
    st.markdown('### Off track percentage')
    # Plot donut chart
    fig = donut_chart(off_track_df)
    st.plotly_chart(fig, use_container_width=True)

#st.markdown('### Consistency')
#prog_fig = progress_bar_chart(workout_consist)
#st.plotly_chart(prog_fig)