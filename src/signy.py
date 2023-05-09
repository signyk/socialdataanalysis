""" Importing packages """
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd

# Bokeh
from bokeh.plotting import show, figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, DatetimeTickFormatter
from bokeh.io import show, output_file

# Local
from utils.make_data import (
    get_data,
    clean_data,
    get_neighborhoods,
    filter_data_years,
    get_hospitals,
)
from utils.const import FILTER_CALL_TYPES, INTERESTING_NEIGHBORHOODS
from utils.plot_functions import (
    make_bokeh_line_plot,
    make_map,
    make_bokeh_tabs,
    make_cal_plot,
)
from utils.help_functions import get_viridis_pallette, format_string

""" Importing data """
dat_raw = get_data()
dat_all_years = clean_data(dat_raw)
dat = filter_data_years(dat_all_years, 2017, 2023)
neighborhoods = get_neighborhoods()
hospitals = get_hospitals()

# print the names of the columns of the data
print(dat.columns)

# """" scatter plot of the response time of all obsverations """
# plot_dat = dat_all_years.copy()
# # Create a column with row numbers
# plot_dat["row_num"] = range(1, len(plot_dat) + 1)
# # Plot the scatter plot
# fig = px.scatter(
#     plot_dat,
#     x="row_num",
#     y="response_time",
#     title="On-scene time of all observations",
#     labels={"row_num": "Row number", "response_time": "On-scene time"},
# )
# fig.update_layout(
#     xaxis=dict(
#         tickmode="array",
#         tickvals=[i for i in range(0, len(plot_dat), 100000)],
#         # text on the form 100k etc.
#         ticktext=[str(i)[:3] + "k" for i in range(0, len(plot_dat), 100000)],
#     )
# )
# fig.show()


""" Plotting the average number of calls per day per month of each year """
plot_dat = dat.copy()
plot_dat = plot_dat.groupby(["call_date"]).size().reset_index(name="Count")
# Group by month and year and calculate the average number of calls per day
plot_dat["Year_month"] = pd.to_datetime(plot_dat["call_date"].dt.strftime("%Y-%m"))
plot_dat = plot_dat.groupby(["Year_month"]).mean().reset_index()

# Create the source for the plot
src = ColumnDataSource(plot_dat)
x_range = (plot_dat["Year_month"].min(), plot_dat["Year_month"].max())

# Create the figure using bokeh
p = figure(
    x_axis_type="datetime",
    x_range=x_range,
    height=500,
    width=800,
    toolbar_location=None,
    title="Average number of calls per day",
)

# Add a line to the plot
p.line(x="Year_month", y="Count", source=src, line_width=2, color="black")

p.y_range.start = 0
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.xaxis.formatter = DatetimeTickFormatter(days="%d %B %Y")

# Add tooltip to the plot with the date and number of calls
hover = HoverTool()
hover.tooltips = [
    ("Period", "@Year_month{%b %Y}"),
    ("Average number of calls", "@Count"),
]
hover.formatters = {"@Year_month": "datetime"}
p.add_tools(hover)

output_file("figs/calls_per_day.html")
show(p)

# The everage number of calls per day in the whole dataset
print("Average number of calls per day in the whole dataset:")
print(dat_all_years.groupby(["call_date"]).size().mean())


""" Plotting a map of San Fransisco showing average response time for each neighborhood """
plot_data = dat.copy()

fig = make_map(plot_data, neighborhoods, column_to_plot="response_time")
# fig.show()
fig.write_html("figs/map_response_neighborhood.html")

""" Plotting a map of San Fransisco showing average transport time for each neighborhood """
# Create a column for the res time in minutes
plot_data["transport_time"] = (
    plot_data["hospital_dttm"] - plot_data["transport_dttm"]
).dt.total_seconds() / 60

fig = make_map(
    plot_data,
    neighborhoods,
    column_to_plot="transport_time",
)

fig2 = go.Figure(fig)
# add marker for the location of all hospitals
fig2.add_trace(
    go.Scattermapbox(
        lat=hospitals["latitude"],
        lon=hospitals["longitude"],
        mode="markers",
        marker=go.scattermapbox.Marker(
            size=10,
            color="red",
        ),
        text=hospitals["name"],
        hoverinfo="text",
    )
)

# fig2.show()
fig2.write_html("figs/map_transport_neighborhood.html")


""" Bokeh plot with tabs showing the average response and transport time by neighborhood over the years"""
plot_dat = dat.copy()
plot_dat["Year"] = plot_dat["received_dttm"].dt.year

p1 = make_bokeh_line_plot(
    plot_dat,
    FILTER_CALL_TYPES,
    "neighborhood",
    "Year",
    "response_time",
    init_legend_items=INTERESTING_NEIGHBORHOODS,
)

p2 = make_bokeh_line_plot(
    plot_dat,
    FILTER_CALL_TYPES,
    "neighborhood",
    "Year",
    "transport_time",
    init_legend_items=INTERESTING_NEIGHBORHOODS,
)
output_file("figs/response_transport_neighborhood_years.html")
tabs_plot = make_bokeh_tabs([p1, p2])
show(tabs_plot)


""" Bokeh plot of the average response time by call type over the years and months"""
plot_dat = dat_all_years.copy()
plot_dat["Year_month"] = pd.to_datetime(plot_dat["received_dttm"].dt.strftime("%Y-%m"))
year_months = plot_dat["Year_month"].unique()

p = make_bokeh_line_plot(
    plot_dat,
    ["Medical Incident", "Structure Fire", "Traffic Collision"],
    "call_type",
    "Year_month",
    "response_time",
    (min(year_months), max(year_months)),
    init_legend_items=["Medical Incident", "Structure Fire", "Traffic Collision"],
)

# Format tooltip to show the date as a string
p.xaxis.formatter = DatetimeTickFormatter(months="%b %Y")
hover = HoverTool(
    tooltips=[
        ("Call type", "$name"),
        ("Time period", "@x_variable{%b %Y}"),
        ("Response time", "@$name{0.00} minutes"),
    ],
    formatters={"@x_variable": "datetime"},
)

# Remove the old hover tool and add the new one
p.tools = []
p.add_tools(hover)

# Change the axis labels
p.xaxis.axis_label = "Time"
p.yaxis.axis_label = "Average response time (minutes)"
p.title.text = "Average response time by call type over months and years"

output_file("figs/bokeh_call_types.html")
show(p)


""" Cal plot of the average response time by call type over the years and months"""
p = make_cal_plot(
    dat=dat,
    filter_call_types=["Medical Incident"],
    filter_years=range(2017, 2023),
    column_name="response_time",
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


"""Bokeh plot showing the average response time by year, split into intake, queue and travel time"""
split_time_data = dat.copy()
split_time_data = split_time_data[
    split_time_data["call_type"].isin(["Medical Incident"])
]

## Create the split times
split_time_data["intake_time"] = (
    split_time_data["entry_dttm"] - split_time_data["received_dttm"]
).dt.total_seconds() / 60
split_time_data["queue_time"] = (
    split_time_data["dispatch_dttm"] - split_time_data["entry_dttm"]
).dt.total_seconds() / 60
split_time_data["travel_time"] = (
    split_time_data["on_scene_dttm"] - split_time_data["dispatch_dttm"]
).dt.total_seconds() / 60

# Remove values that are negative
split_time_data = split_time_data[
    (split_time_data["intake_time"] >= 0)
    & (split_time_data["queue_time"] >= 0)
    & (split_time_data["travel_time"] >= 0)
]


# Create the year variable
split_time_data["Year"] = split_time_data["received_dttm"].dt.year.astype(str)

# Transform the data to long format
long = split_time_data.melt(
    id_vars="Year",
    value_vars=["intake_time", "queue_time", "travel_time"],
    var_name="Time",
    value_name="minutes",
)

# Calculate the mean time per year for all split times
res = long.groupby(["Time", "Year"])["minutes"].mean().reset_index(name="mean")

# Pivot the data to wide format
processed_dat = res.pivot(index="Year", columns="Time", values="mean").reset_index()

# Create the source for the plot
descripts = [d for d in list(long["Time"].unique()) if not pd.isna(d)]
src = ColumnDataSource(processed_dat)
x_range = processed_dat["Year"].unique().tolist()
viridis = get_viridis_pallette(len(descripts))

# Stacked bar chart
p = figure(
    x_range=x_range,
    height=500,
    width=800,
    title="Average response time per year",
    toolbar_location=None,
    tools="hover",
    tooltips=[
        ("Type", "$name"),
        ("Year", "@Year"),
        ("Time", "@$name"),
    ],
)

p.vbar_stack(
    descripts,
    x="Year",
    width=0.9,
    source=src,
    color=viridis,
    legend_label=[format_string(d) for d in descripts],
)

p.y_range.start = 0
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.location = "top_right"
p.legend.orientation = "vertical"
p.add_layout(p.legend[0], "right")

output_file("figs/split_time.html")
show(p)

""" Bokeh plot showing the average response and transport time by time of day and day over the years """
plot_dat = dat.copy()
plot_dat["Year"] = plot_dat["received_dttm"].dt.year  # .astype(str)

p1 = make_bokeh_line_plot(
    plot_dat,
    ["Medical Incident"],
    "period_of_day",
    "Year",
    "response_time",
    init_legend_items=plot_dat["period_of_day"].unique().tolist(),
)

p2 = make_bokeh_line_plot(
    plot_dat,
    ["Medical Incident"],
    "period_of_day",
    "Year",
    "transport_time",
    init_legend_items=plot_dat["period_of_day"].unique().tolist(),
)

output_file("figs/response_transport_day_period.html")
tabs_plot = make_bokeh_tabs([p1, p2])
show(tabs_plot)
