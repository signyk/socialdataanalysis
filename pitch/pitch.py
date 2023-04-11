""" Importing packages """
import datetime as dt
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
import folium
import plotly.express as px

from utils.make_data import get_data

""" Importing data """
dat = get_data()
# print the names of the columns of the data
print(dat.columns)
# print number of rows and columns
print(dat.shape)
# Number of unique values in the column "Call Number"
print(dat["Call Number"].nunique())
# Unique values in the column "Call Type"
print(dat["Call Type"].unique())

""" Clean up the location data """
# extract the latitude and longitude from the case_location column and add them as seperate columns
location = dat["case_location"].str.extract(r"\((.+)\)")
dat["latitude"] = location[0].str.split(" ").str[0]
dat["longitude"] = location[0].str.split(" ").str[1]
# convert the latitude and longitude columns to numeric
dat["latitude"] = pd.to_numeric(dat["latitude"])
dat["longitude"] = pd.to_numeric(dat["longitude"])
# drop the case_location column
dat = dat.drop(columns=["case_location"])

""" Create heatmap of incidents """
# done in pitch_heatmap.ipynb

""" Create a histrogram of the number of incidents per weekday """
weekday_map = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}
# Create a new column with the weekday of the incident
dat_unique = dat.drop_duplicates(subset="Incident Number")
dat_unique["weekday"] = dat_unique["Call Date"].dt.weekday.map(weekday_map)

fig = px.histogram(
    dat_unique,
    x="weekday",
    category_orders=dict(weekday=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
    labels={"weekday": "Weekday"},
    title="Number of incidents per weekday",
    color_discrete_sequence=["#FF914D"],
).update_layout(yaxis_title="Number of incidents")
fig.show()


""" Create a histrogram of the number of incidents per district """
dat_unique = dat.drop_duplicates(subset="Incident Number")
# Create a histogram showing the number of incidents per district
DISTRICTS = [
    "Tenderloin",
    "South of Market",
    "Mission",
    "Financial District/South Beach",
    "Bayview Hunters Point",
    "Sunset/Parkside",
    " Western Addition",
    "Nob Hill",
    "Castro/Upper Market",
    "Hayes Valley",
    "Outer Richmond",
]
# Filter the data to only contain the districts in DISTRICTS
dat_unique = dat_unique[
    dat_unique["Neighborhooods - Analysis Boundaries"].isin(DISTRICTS)
]
# Create a histogram showing the number of incidents per district

fig = px.histogram(
    dat_unique,
    x="Neighborhooods - Analysis Boundaries",
    labels={"Neighborhooods - Analysis Boundaries": "District"},
    title="Number of incidents per district",
    color_discrete_sequence=["#FFE765"],
).update_layout(yaxis_title="Number of incidents")
fig.show()
