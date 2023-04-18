""" Importing packages """
import datetime as dt
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
import folium
import plotly.express as px

from utils.make_data import get_data, clean_data

""" Importing data """
dat_raw = get_data()
dat = clean_data(dat_raw)

# print the names of the columns of the data
print(dat.columns)
