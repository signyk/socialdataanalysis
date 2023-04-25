""" Importing packages """
import datetime as dt
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
import folium
import plotly.express as px
import matplotlib.pyplot as plt

from utils.make_data import get_data, clean_data, get_neighborhoods

""" Importing data """
dat_raw = get_data()
dat = clean_data(dat_raw)
neighborhoods = get_neighborhoods()

# print the names of the columns of the data
print(dat.columns)

""" Plotting a map of San Fransisco showing average response time for each neighborhood """
mean_response = (
    dat.groupby("neighborhood", as_index=False)["on_scene_time"].mean()
    # .rename(columns={"neighborhood": "nhood", "on_scene_time": "on_scene_time"})
)

fig = px.choropleth_mapbox(
    mean_response,
    geojson=neighborhoods,
    locations="neighborhood",
    color="on_scene_time",
    color_continuous_scale="Viridis",
    range_color=(0, max(mean_response["on_scene_time"])),
    mapbox_style="carto-positron",
    zoom=11,
    center={"lat": 37.773972, "lon": -122.431297},
    opacity=0.5,
    labels={"on_scene_time": "on_scene_time"},
)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
