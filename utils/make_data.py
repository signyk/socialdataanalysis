""" Importing packages """
import datetime as dt
import pandas as pd
import json


def create_data():
    """Read in the raw data and clean it. Write out a clean csv file"""
    raw_dat = pd.read_csv("data/fireIncidents.csv")
    # Create a copy of the data to clean
    dat = raw_dat.copy()

    """ Clean data """
    # Convert Call Date to datetime
    dat["Call Date"] = pd.to_datetime(dat["Call Date"], format="%m/%d/%Y")

    # Only keep data from 2012 to 2023
    dat = dat.loc[dat["Call Date"] < dt.datetime(2023, 1, 1)]
    dat = dat.loc[dat["Call Date"] >= dt.datetime(2012, 1, 1)]

    # Convert the rest of the date columns to datetime
    dat["Watch Date"] = pd.to_datetime(dat["Watch Date"], format="%m/%d/%Y")
    dat["Received DtTm"] = pd.to_datetime(
        dat["Received DtTm"], format="%m/%d/%Y %H:%M:%S %p"
    )
    dat["Entry DtTm"] = pd.to_datetime(dat["Entry DtTm"], format="%m/%d/%Y %H:%M:%S %p")
    dat["Dispatch DtTm"] = pd.to_datetime(
        dat["Dispatch DtTm"], format="%m/%d/%Y %H:%M:%S %p"
    )
    dat["Dispatch DtTm"] = pd.to_datetime(
        dat["Dispatch DtTm"], format="%m/%d/%Y %H:%M:%S %p"
    )
    dat["Response DtTm"] = pd.to_datetime(
        dat["Response DtTm"], format="%m/%d/%Y %H:%M:%S %p"
    )
    dat["On Scene DtTm"] = pd.to_datetime(
        dat["On Scene DtTm"], format="%m/%d/%Y %H:%M:%S %p"
    )
    dat["Transport DtTm"] = pd.to_datetime(
        dat["Transport DtTm"], format="%m/%d/%Y %H:%M:%S %p"
    )
    dat["Hospital DtTm"] = pd.to_datetime(
        dat["Hospital DtTm"], format="%m/%d/%Y %H:%M:%S %p"
    )
    dat["Available DtTm"] = pd.to_datetime(
        dat["Available DtTm"], format="%m/%d/%Y %H:%M:%S %p"
    )

    # write out a csv file called "fireIncidents_clean.csv"
    dat.to_csv("data/fireIncidents_clean.csv", index=False)


def get_data():
    """Read in the cleaned data"""
    parse_dates = [
        "Call Date",
        "Watch Date",
        "Received DtTm",
        "Entry DtTm",
        "Dispatch DtTm",
        "Response DtTm",
        "On Scene DtTm",
        "Transport DtTm",
        "Hospital DtTm",
        "Available DtTm",
    ]
    dat = pd.read_csv(
        "data/fireIncidents_clean.csv", parse_dates=parse_dates, low_memory=False
    )
    return dat


def get_neighborhoods():
    """Read in the neighborhoods data"""
    f = open("data/neighborhoods.geojson", "r")
    neighborhoods = json.load(f)
    # Add an id to each neighborhood
    for f in neighborhoods["features"]:
        f["id"] = f["properties"]["nhood"]

    return neighborhoods


def clean_data(dat: pd.DataFrame) -> pd.DataFrame:
    "Dropping columns"
    # Drop the columns that are not needed
    dat_clean = dat.drop(
        [
            "Box",
            "Original Priority",
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

    """ Create a column for the hour of the day """
    dat_clean["hour"] = dat_clean["received_dttm"].dt.hour
    # create bins for the hour of the day
    bins = [-1, 6, 12, 18, 24]
    labels = ["Night", "Morning", "Afternoon", "Evening"]
    dat_clean["period_of_day"] = pd.cut(dat_clean["hour"], bins=bins, labels=labels)

    "Drop rows"
    # Drop the rows with call_final_disposition == "Cancelled" or "Duplicate"
    dat_clean = dat_clean.loc[
        (dat_clean["call_final_disposition"] != "Cancelled")
        & (dat_clean["call_final_disposition"] != "Duplicate")
    ]

    # Drop the rows with on_scene_dttm == NaT
    dat_clean = dat_clean.loc[dat_clean["on_scene_dttm"].notna()]

    "Create time columns"
    # Create a column for the on scene time in minutes
    dat_clean["on_scene_time"] = (
        dat_clean["on_scene_dttm"] - dat_clean["received_dttm"]
    ).dt.total_seconds() / 60

    # Drop rows where on_scene_time is unlikely
    dat_clean = dat_clean.loc[dat_clean["on_scene_time"] >= 0]
    dat_clean = dat_clean.loc[dat_clean["on_scene_time"] <= 720]

    # Create a column for the transport time in minutes
    dat_clean["transport_time"] = (
        dat_clean["hospital_dttm"] - dat_clean["transport_dttm"]
    ).dt.total_seconds() / 60

    # Drop rows where transport_time is unlikely
    dat_clean = dat_clean.loc[dat_clean["transport_time"] >= 0]
    dat_clean = dat_clean.loc[dat_clean["transport_time"] <= 720]

    return dat_clean
