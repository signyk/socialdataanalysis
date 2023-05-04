""" Importing packages """
import folium
import plotly.express as px

# Bokeh
from bokeh.plotting import show
from bokeh.io import show

# Local
from utils.make_data import get_data, clean_data, get_neighborhoods
from utils.const import FIRE_CALL_TYPES
from utils.plot_functions import make_bokeh_line_plot

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


""" Bokeh plot of the avaerage response time by neighborhood over the years"""
plot_dat = dat.copy()
plot_dat["Year"] = plot_dat["received_dttm"].dt.year  # .astype(str)

p = make_bokeh_line_plot(
    plot_dat,
    "bokeh_neighborhoods.html",
    FIRE_CALL_TYPES,
    "neighborhood",
    "Year",
    (2012, 2022),
)
show(p)

""" Bokeh plot of the avaerage response time by call type over the years"""
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
    year_months,
)
show(p)
