""" Importing packages """
import datetime as dt
import pandas as pd

""" Reading data """
create_data = False
if create_data:
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
    dat = pd.read_csv("data/fireIncidents_clean.csv")
    return dat
