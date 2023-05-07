""" Importing packages """
import folium
import plotly.express as px
import matplotlib.pyplot as plt

# Bokeh
from bokeh.plotting import show
from bokeh.io import show, output_file

# Local
from utils.make_data import get_data, clean_data, get_neighborhoods
from utils.const import FILTER_CALL_TYPES
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

fig = make_map(plot_data, neighborhoods, column_to_plot="on_scene_time")
fig.show()
fig.write_html("figs/map_response_neighborhood.html")

""" Plotting a map of San Fransisco showing average transport time for each neighborhood """
# Create a column for the on scene time in minutes
plot_data["transport_time"] = (
    plot_data["hospital_dttm"] - plot_data["transport_dttm"]
).dt.total_seconds() / 60

fig = make_map(
    plot_data,
    neighborhoods,
    column_to_plot="transport_time",
)
fig.show()
fig.write_html("figs/map_transport_neighborhood.html")


""" Bokeh plot with tabs showing the average response and transport time by neighborhood over the years"""
plot_dat = dat.copy()
plot_dat["Year"] = plot_dat["received_dttm"].dt.year  # .astype(str)

p1 = make_bokeh_line_plot(
    plot_dat,
    "bokeh_response_neighborhoods.html",
    FILTER_CALL_TYPES,
    "neighborhood",
    "Year",
    "on_scene_time",
    (2012, 2022),
)

p2 = make_bokeh_line_plot(
    plot_dat,
    "bokeh_transport_neighborhoods.html",
    FILTER_CALL_TYPES,
    "neighborhood",
    "Year",
    "transport_time",
    (2012, 2022),
)
output_file("figs/response_transport_neighborhood_years.html")
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
    FILTER_CALL_TYPES,
    "call_type",
    "Year_month",
    "on_scene_time",
    year_months,
)
show(p)


""" Cal plot of the average response time by call type over the years and months"""
p = make_cal_plot(
    dat=dat,
    filter_call_types=["Medical Incident"],
    filter_years=range(2017, 2023),
    column_name="on_scene_time",
)
plt.savefig("figs/calplot_response.png", bbox_inches="tight")
p.show()

""" Cal plot of the average transport time by call type over the years and months"""
p = make_cal_plot(
    dat=dat,
    filter_call_types=["Medical Incident"],
    filter_years=range(2017, 2023),
    column_name="transport_time",
)
plt.savefig("figs/calplot_transport.png", bbox_inches="tight")
p.show()
