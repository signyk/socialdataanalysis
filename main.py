""" Importing packages """
import datetime as dt
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save

from utils.make_data import get_data

""" Importing data """
dat = get_data()
# print the names of the columns of the data
print(dat.columns)
# print number of rows and columns
print(dat.shape)

# Number of unique values in the column "Call Number"
print(dat["Call Number"].nunique())
print(dat["Call Type"].unique())
