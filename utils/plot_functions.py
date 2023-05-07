""" Importing packages """
import pandas as pd
import plotly.express as px
from typing import List
import calplot

# Bokeh
from bokeh.models import TabPanel, Tabs
from bokeh.models import ColumnDataSource, Legend
from bokeh.plotting import figure
from bokeh.io import output_file

# Local
from utils.help_functions import get_viridis_pallette
from utils.const import FIRE_CALL_TYPES


def make_map(
    dat: pd.DataFrame,
    neighborhoods: dict,
    column_to_plot: str = "on_scene_time",
    scale_name: str = "On Scene Time",
):
    """Plotting a map of San Fransisco showing average response time for each neighborhood"""
    mean_response = (
        dat.groupby("neighborhood", as_index=False)[column_to_plot]
        .mean()
        .rename(columns={"neighborhood": "Neighborhood", column_to_plot: scale_name})
    )

    fig = px.choropleth_mapbox(
        mean_response,
        geojson=neighborhoods,
        locations="Neighborhood",
        color=scale_name,
        color_continuous_scale="Viridis",
        range_color=(min(mean_response[scale_name]), max(mean_response[scale_name])),
        mapbox_style="carto-positron",
        zoom=11,
        center={"lat": 37.773972, "lon": -122.431297},
        opacity=0.5,
        # labels={"On Scene Time": "On Scene Time"},
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def make_bokeh_line_plot(
    dat: pd.DataFrame,
    filename: str = "bokeh1.html",
    filter_call_types: list = FIRE_CALL_TYPES,
    color_var: str = "neighborhood",
    x_var: str = "Year",
    y_var: str = "on_scene_time",
    x_range: tuple = (2012, 2022),
):
    full_path = "figs/" + filename
    output_file(full_path)
    dat_fire = dat[dat["call_type"].isin(filter_call_types)]
    dat_fire = dat_fire[dat_fire[color_var].notna()]
    dat_fire["x_variable"] = dat_fire[x_var]
    dat_fire["y_variable"] = dat_fire[y_var]

    res = (
        dat_fire.groupby([color_var, "x_variable"])["y_variable"]
        .mean()
        .reset_index(name="mean")
    )
    processed_dat = res.pivot(
        index="x_variable", columns=color_var, values="mean"
    ).reset_index()

    descripts = [d for d in list(dat_fire[color_var].unique()) if not pd.isna(d)]
    src = ColumnDataSource(processed_dat)
    src.column_names
    viridis = get_viridis_pallette(len(descripts))
    p = figure(
        x_range=x_range,
        height=500,
        width=800,
        title=y_var,
        toolbar_location=None,
        tools="hover",
        tooltips=[
            (color_var, "$name"),
            (x_var, "@x_variable"),
            (y_var, "@$name"),
        ],
    )

    items = []  # for the custom legend
    lines = {}  # to store the lines

    for indx, i in enumerate(descripts):
        ### Create a line for each district
        lines[i] = p.line(
            x="x_variable",
            y=i,
            source=src,
            alpha=0.9,
            muted_alpha=0.07,
            width=1.2,
            color=viridis[indx],
            name=i,
        )
        items.append((i, [lines[i]]))
        lines[i].visible = True if i == list(descripts)[0] else False

    legend1 = Legend(items=items[:34], location=(0, 10))
    legend2 = Legend(items=items[34:], location=(0, 10))
    p.add_layout(legend1, "right")
    p.add_layout(legend2, "right")
    p.legend.click_policy = "hide"  # or "mute"
    p.xaxis.axis_label = x_var
    p.yaxis.axis_label = y_var
    p.y_range.only_visible = True
    p.y_range.start = 0
    # p.sizing_mode = "scale_width"

    return p


def make_cal_plot(
    dat: pd.DataFrame,
    filter_call_types: list = ["Medical Incident"],
    filter_years: list = range(2017, 2023),
    column_name: str = "on_scene_time",
    title: str = "On Scene Time",
):
    caldat = dat.copy()
    caldat = caldat[caldat["call_type"].isin(filter_call_types)]
    caldat = caldat[caldat["received_dttm"].dt.year.isin(filter_years)]
    # Select the relevant columns ("received_dttm" and column_name)
    caldat = caldat[["received_dttm", column_name]]
    # Set the index to be the date
    caldat = caldat.set_index("received_dttm")
    # Make the plot
    fig, ax = calplot.calplot(
        data=caldat[column_name],
        how="mean",
        cmap="YlGnBu",
        # fillcolor="grey",
        suptitle=title,
        linewidth=0.2,
    )

    return fig


def make_bokeh_tabs(figs: List[figure]):
    """Creates a tabbed layout of bokeh figures"""
    tabs = Tabs(
        tabs=[TabPanel(child=fig, title=f"Tab {i}") for i, fig in enumerate(figs)]
    )
    return tabs
