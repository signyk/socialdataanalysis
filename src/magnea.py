""" Importing packages """
import datetime as dt
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
import folium
import plotly.express as px

from utils.make_data import get_data, get_on_scene_map
from utils.make_data import get_on_scene_map
import json

import matplotlib.pyplot as plt

""" Importing data """


def clean_data(dat: pd.DataFrame) -> pd.DataFrame:
    "Dropping columns"
    # Drop the columns that are not needed
    dat_clean = dat.drop(
        [
            "Box",
            "Original Priority",
            "Priority",
            "Final Priority",
            "Zipcode of Incident",
            "Fire Prevention District",
            "Supervisor District",
            "Analysis Neighborhoods",
            "City",
        ],
        axis=1,
    )
    "Clean up the location column"
    # extract the latitude and longitude from the case_location column and add them as seperate columns
    location = dat_clean["case_location"].str.extract(r"\((.+)\)")
    dat_clean["latitude"] = location[0].str.split(" ").str[0]
    dat_clean["longitude"] = location[0].str.split(" ").str[1]
    # convert the latitude and longitude columns to numeric
    dat_clean["latitude"] = pd.to_numeric(dat_clean["latitude"])
    dat_clean["longitude"] = pd.to_numeric(dat_clean["longitude"])
    # drop the case_location column
    dat_clean = dat_clean.drop(columns=["case_location"])

    "Rename columns"
    dat_clean = dat_clean.rename(
        columns={
            "Call Number": "call_number",
            "Unit ID": "unit_id",
            "Incident Number": "incident_number",
            "Call Type": "call_type",
            "Call Date": "call_date",
            "Watch Date": "watch_date",
            "Received DtTm": "received_dttm",
            "Entry DtTm": "entry_dttm",
            "Dispatch DtTm": "dispatch_dttm",
            "Response DtTm": "response_dttm",
            "On Scene DtTm": "on_scene_dttm",
            "Transport DtTm": "transport_dttm",
            "Hospital DtTm": "hospital_dttm",
            "Call Final Disposition": "call_final_disposition",
            "Available DtTm": "available_dttm",
            "Address": "address",
            "Battalion": "battalion",
            "Station Area": "station_area",
            "ALS Unit": "als_unit",
            "Call Type Group": "call_type_group",
            "Number of Alarms": "number_of_alarms",
            "Unit Type": "unit_type",
            "Unit sequence in call dispatch": "unit_sequence",
            "Neighborhooods - Analysis Boundaries": "neighborhood",
            "RowID": "row_id",
            "latitude": "latitude",
            "longitude": "longitude",
        }
    )

    "Drop rows"
    # Drop the rows with call_final_disposition == "Cancelled" or "Duplicate"
    dat_clean = dat_clean.loc[
        (dat_clean["call_final_disposition"] != "Cancelled")
        & (dat_clean["call_final_disposition"] != "Duplicate")
    ]

    # Drop the rows with on_scene_dttm == NaT
    dat_clean = dat_clean.loc[dat_clean["on_scene_dttm"].notna()]

    return dat_clean


def get_on_scene_map(dat: pd.DataFrame) -> pd.DataFrame:
    "Map incident_number to on_scene_time"
    # Create a column for the on scene time in minutes
    dat["on_scene_time"] = (
        dat["on_scene_dttm"] - dat["received_dttm"]
    ).dt.total_seconds() / 60

    # Drop rows where on_scene_time < 0 (these are errors, AM/PM confusion)
    dat = dat.loc[dat["on_scene_time"] >= 0]
    return dat


dat_raw = get_data()
dat = clean_data(dat_raw)

# print the names of the columns of the data
print(dat.columns)

dat = get_on_scene_map(dat)
print(dat.on_scene_time)

print(dat.neighborhood.nunique())


f = open(
    "/Users/magnea/Desktop/DTU/Social Data/socialdataanalysis/data/Analysis Neighborhoods.geojson"
)
neighborhoods = json.load(f)


""" Plotting a map of San Fransisco showing average response time for each neighborhood """
mean_response = (
    dat.groupby("neighborhood", as_index=False)["on_scene_time"]
    .mean()
    .rename(columns={"neighborhood": "nhood", "on_scene_time": "on_scene_time"})
)

fig = px.choropleth_mapbox(
    mean_response,
    geojson=neighborhoods,
    locations="nhood",
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
fig.write_html("map.html")


""" Stat analysis of response time """

p = dat["on_scene_time"].plot(kind="bar")
p.show()

counts, bins = np.histogram(dat["on_scene_time"])
plt.hist(bins[:-1], bins, weights=counts)
