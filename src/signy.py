""" Importing packages """
import datetime as dt
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import matplotlib.pyplot as plt

# Bokeh
from bokeh.models import ColumnDataSource, FactorRange, Legend, HoverTool
from bokeh.plotting import figure, show, save
from bokeh.io import output_file, show

# Local
from utils.make_data import get_data, clean_data, get_neighborhoods
from utils.help_functions import get_viridis_pallette
from utils.const import FIRE_CALL_TYPES

""" Importing data """
dat_raw = get_data()
dat = clean_data(dat_raw)
neighborhoods = get_neighborhoods()

# print the names of the columns of the data
print(dat.columns)

""" Plotting a map of San Fransisco showing average response time for each neighborhood """
mean_response = (
    dat.groupby("neighborhood", as_index=False)["on_scene_time"]
    .mean()
    .rename(columns={"neighborhood": "Neighborhood", "on_scene_time": "On Scene Time"})
)

fig = px.choropleth_mapbox(
    mean_response,
    geojson=neighborhoods,
    locations="Neighborhood",
    color="On Scene Time",
    color_continuous_scale="Viridis",
    range_color=(0, max(mean_response["On Scene Time"])),
    mapbox_style="carto-positron",
    zoom=11,
    center={"lat": 37.773972, "lon": -122.431297},
    opacity=0.5,
    # labels={"On Scene Time": "On Scene Time"},
)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()


""" Bokeh plot """
output_file("figs/bokeh1.html")
dat_fire = dat[dat["call_type"].isin(FIRE_CALL_TYPES)]
dat_fire = dat_fire[dat_fire["neighborhood"].notna()]
dat_fire["Year"] = dat_fire["received_dttm"].dt.year  # .astype(str)

res = (
    dat_fire.groupby(["neighborhood", "Year"])["on_scene_time"]
    .mean()
    .reset_index(name="mean")
)
processed_dat = res.pivot(
    index="Year", columns="neighborhood", values="mean"
).reset_index()

descripts = [d for d in list(dat["neighborhood"].unique()) if not pd.isna(d)]
src = ColumnDataSource(processed_dat)
years = [i for i in range(2012, 2022)]
viridis = get_viridis_pallette(len(descripts))
p = figure(
    # x_range=years,
    x_range=(2012, 2022),
    height=500,
    width=800,
    title="Average response time by neighborhood by years",
    toolbar_location=None,
    tools="hover",
    tooltips=[
        ("Neighborhood", "$name"),
        ("Year", "@Year"),
        ("Average response time", "@$name"),
    ],
)

items = []  # for the custom legend
lines = {}  # to store the lines

for indx, i in enumerate(descripts):
    ### Create a line for each district
    lines[i] = p.line(
        x="Year",
        y=i,
        source=src,
        alpha=0.9,
        muted_alpha=0.07,
        width=1.2,
        color=viridis[indx],
        name=i,
    )
    items.append((i, [lines[i]]))
    lines[i].visible = True if i == list(descripts)[0] else False

legend1 = Legend(items=items[:34], location=(0, 10))
legend2 = Legend(items=items[34:], location=(0, 10))
p.add_layout(legend1, "right")
p.add_layout(legend2, "right")
p.legend.click_policy = "hide"  # or "mute"
p.xaxis.axis_label = "Year"
p.yaxis.axis_label = "Average response time"
p.y_range.only_visible = True
p.y_range.start = 0
p.sizing_mode = "scale_width"

show(p)
