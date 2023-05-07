""" Importing packages """
import folium
import plotly.express as px

# Bokeh
from bokeh.plotting import show
from bokeh.io import show

# Local
from utils.make_data import get_data, clean_data, get_neighborhoods
from utils.const import FIRE_CALL_TYPES
from utils.plot_functions import (
    make_bokeh_line_plot,
    make_map,
    make_bokeh_tabs,
    make_cal_plot,
)

""" Importing data """
dat_raw = get_data()
dat = clean_data(dat_raw)
neighborhoods = get_neighborhoods()

# print the names of the columns of the data
print(dat.columns)

""" Plotting a map of San Fransisco showing average response time for each neighborhood """
plot_data = dat.copy()

fig = make_map(
    plot_data,
    neighborhoods,
    column_to_plot="on_scene_time",
    scale_name="On Scene Time",
)
fig.show()

""" Plotting a map of San Fransisco showing average transport time for each neighborhood """
# Create a column for the on scene time in minutes
plot_data["transport_time"] = (
    plot_data["hospital_dttm"] - plot_data["transport_dttm"]
).dt.total_seconds() / 60

fig = make_map(
    plot_data,
    neighborhoods,
    column_to_plot="transport_time",
    scale_name="Transport Time",
)
fig.show()


""" Bokeh plot with tabs showing the average response and transport time by neighborhood over the years"""
plot_dat = dat.copy()
plot_dat["Year"] = plot_dat["received_dttm"].dt.year  # .astype(str)

p1 = make_bokeh_line_plot(
    plot_dat,
    "bokeh_neighborhoods.html",
    FIRE_CALL_TYPES,
    "neighborhood",
    "Year",
    "on_scene_time",
    (2012, 2022),
)

p2 = make_bokeh_line_plot(
    plot_dat,
    "bokeh_neighborhoods.html",
    FIRE_CALL_TYPES,
    "neighborhood",
    "Year",
    "transport_time",
    (2012, 2022),
)

tabs_plot = make_bokeh_tabs([p1, p2])
show(tabs_plot)

""" Bokeh plot of the average response time by call type over the years and months"""
plot_dat = dat.copy()
plot_dat["Year_month"] = plot_dat["received_dttm"].dt.to_period("M").astype(str)
year_months = [
    "-".join([str(i), str(j).zfill(2)]) for i in range(2012, 2022) for j in range(1, 13)
]

p = make_bokeh_line_plot(
    plot_dat,
    "bokeh_call_types.html",
    FIRE_CALL_TYPES,
    "call_type",
    "Year_month",
    "on_scene_time",
    year_months,
)
show(p)

""" Bokeh plot of the average response time by call type over the years and months"""
p = make_cal_plot(
    dat=dat,
    filter_call_types=["Medical Incident"],
    filter_years=range(2017, 2023),
    column_name="on_scene_time",
    title="Average response time",
)
p.show()

""" Bokeh plot of the average transport time by call type over the years and months"""
p = make_cal_plot(
    dat=dat,
    filter_call_types=["Medical Incident"],
    filter_years=range(2017, 2023),
    column_name="transport_time",
    title="Average transport time",
)
p.show()
