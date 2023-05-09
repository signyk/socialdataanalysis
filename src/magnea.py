""" Importing packages """
import datetime as dt
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
import folium
import plotly.express as px

from utils.make_data import get_data, get_on_scene_map, clean_data
import json

from matplotlib.pyplot import figure, title, subplot, plot, hist, show

""" Importing data """

dat_raw = get_data()
dat = clean_data(dat_raw)

# print the names of the columns of the data
print(dat.columns)

get_on_scene_map(dat)
print(dat.response_time)
dat = dat.loc[dat["response_time"] >= 0]
dat = dat.loc[dat["response_time"] < 720]
print(dat[dat["response_time"] < 0])

print(dat.neighborhood.nunique())
print(dat.neighborhood.value_counts())

f = open(
    "/Users/magnea/Desktop/DTU/Social Data/socialdataanalysis/data/Analysis Neighborhoods.geojson"
)
neighborhoods = json.load(f)


""" Plotting a map of San Fransisco showing average response time for each neighborhood """
mean_response = (
    dat.groupby("neighborhood", as_index=False)["response_time"]
    .mean()
    .rename(columns={"neighborhood": "nhood", "response_time": "response_time"})
)

fig = px.choropleth_mapbox(
    mean_response,
    geojson=neighborhoods,
    locations="nhood",
    color="response_time",
    color_continuous_scale="Viridis",
    range_color=(0, max(mean_response["response_time"])),
    mapbox_style="carto-positron",
    zoom=11,
    center={"lat": 37.773972, "lon": -122.431297},
    opacity=0.5,
    labels={"response_time": "response_time"},
)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
fig.write_html("map.html")


""" Stat analysis of response time """


tenderloin = dat[dat["neighborhood"] == "Tenderloin"]
# tenderloin = tenderloin[tenderloin["response_time"]<70]
min(tenderloin["response_time"])

nbins = 400
figure(figsize=(12, 4))
title("Normal distribution")
subplot(1, 2, 1)
plot(tenderloin["response_time"], ".")
subplot(1, 3, 3)
hist(tenderloin["response_time"], bins=nbins)
show()


excelsior = dat[dat["neighborhood"] == "Excelsior"]
# excelsior = excelsior[excelsior["response_time"]<350]
min(excelsior["response_time"])

nbins = 400
figure(figsize=(12, 4))
title("Normal distribution")
subplot(1, 2, 1)
plot(excelsior["response_time"], ".")
subplot(1, 3, 3)
hist(excelsior["response_time"], bins=nbins)
show()


test = dat[dat["response_time"] > 720]
print(test.shape)
print(dat.shape)
