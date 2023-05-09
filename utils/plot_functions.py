""" Importing packages """
from math import pi
import pandas as pd
import plotly.express as px
from typing import List
import calplot
import seaborn as sns

# Bokeh
from bokeh.models import TabPanel, Tabs
from bokeh.models import ColumnDataSource, Legend, HoverTool
from bokeh.plotting import figure
from bokeh.io import output_file, output_notebook

# Local
from utils.help_functions import get_viridis_pallette, format_string
from utils.const import FILTER_CALL_TYPES


def make_map(
    dat: pd.DataFrame,
    neighborhoods: dict,
    column_to_plot: str = "response_time",
):
    """Plotting a map of San Fransisco showing average response time for each neighborhood"""
    mean_response = (
        dat.groupby("neighborhood", as_index=False)[column_to_plot]
        .mean()
        .rename(
            columns={
                "neighborhood": "Neighborhood",
            }
        )
    )

    fig = px.choropleth_mapbox(
        mean_response,
        geojson=neighborhoods,
        locations="Neighborhood",
        color=column_to_plot,
        color_continuous_scale="Viridis",
        range_color=(
            min(mean_response[column_to_plot]),
            max(mean_response[column_to_plot]),
        ),
        mapbox_style="carto-positron",
        zoom=11,
        center={"lat": 37.773972, "lon": -122.431297},
        opacity=0.5,
        labels={column_to_plot: format_string(column_to_plot)},
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def make_bokeh_line_plot(
    dat: pd.DataFrame,
    filter_call_types: list = FILTER_CALL_TYPES,
    color_var: str = "neighborhood",
    x_var: str = "Year",
    y_var: str = "response_time",
    x_range: tuple = (2017, 2022),
    init_legend_items: List[str] = [],
):
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
        height=600,
        width=1000,
        title=format_string(y_var),
        toolbar_location=None,
        tools="hover",
        tooltips=[
            (format_string(color_var), "$name"),
            (format_string(x_var), "@x_variable"),
            (format_string(y_var), "@$name"),
        ],
    )

    items = []  # for the custom legend
    lines = {}  # to store the lines
    if len(init_legend_items) < 1:
        init_legend_items = [descripts[0]]

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
        lines[i].visible = True if i in init_legend_items else False

    legend1 = Legend(items=items[:21], location=(0, 10))
    legend2 = Legend(items=items[21:], location=(0, 10))
    # legend3 = Legend(items=items[30:], location=(0, 10))
    p.add_layout(legend1, "right")
    p.add_layout(legend2, "right")
    p.legend.click_policy = "hide"  # or "mute"
    p.xaxis.axis_label = format_string(x_var)
    p.yaxis.axis_label = format_string(y_var)
    p.y_range.only_visible = True
    p.y_range.start = 0
    # p.sizing_mode = "scale_width"

    return p


def make_cal_plot(
    dat: pd.DataFrame,
    filter_call_types: list = ["Medical Incident"],
    filter_years: list = range(2017, 2023),
    column_name: str = "response_time",
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
        suptitle=format_string(column_name),
        linewidth=0.2,
    )

    return fig


def make_bokeh_tabs(figs: List[figure]):
    """Creates a tabbed layout of bokeh figures"""
    # Set tab titles as the figure titles
    tabs = [TabPanel(child=fig, title=fig.title.text) for fig in figs]
    # Create a Tabs layout
    tabs = Tabs(tabs=tabs)
    return tabs


def make_boxplot(
    dat: pd.DataFrame,
    filter_call_types: list = ["Medical Incident"],
    filter_years: list = None,
    x_var: str = "neighborhood",
    y_var: str = "response_time",
):
    plot_dat = dat[dat["call_type"].isin(filter_call_types)]
    if filter_years:
        plot_dat = plot_dat[plot_dat["received_dttm"].dt.year.isin(filter_years)]
    b = sns.boxplot(data=plot_dat, x=x_var, y=y_var, showfliers=False)
    b.set(xlabel=format_string(x_var), ylabel=format_string(y_var))
    b.set_xticklabels(b.get_xticklabels(), rotation=90)

    return b


def plot_importance(
    column_names: List[str], importances: List[float], title="Importance of Features"
):
    # Create a dataframe from the feature importances
    feature_importances = pd.DataFrame(
        {"feature": column_names, "importance": importances}
    )

    # Create a ColumnDataSource from the dataframe
    source = ColumnDataSource(feature_importances)

    # Create a figure with a datetime type x-axis
    p = figure(
        x_range=feature_importances["feature"],
        height=500,
        width=800,
        title=title,
        toolbar_location=None,
    )

    # Add plot elements
    p.vbar(
        x="feature",
        top="importance",
        source=source,
        width=0.70,
        color="firebrick",
        alpha=0.7,
    )

    # Rotate x-axis labels
    p.xaxis.major_label_orientation = pi / 2
    # Add interactivity
    hover = HoverTool()
    hover.tooltips = [("Feature", "@feature"), ("Importance", "@importance{0.000}")]
    p.add_tools(hover)

    return p


def plot_importance2(importance_df: pd.DataFrame, top_n: int = 10):
    """Plot the top_n most important features from a dataframe of feature importances
    where the column names denote the method used to calculate the importance."""

    plot_data = importance_df.reset_index().rename(columns={"index": "Feature"})
    plot_data = plot_data.dropna(axis=1, how="all")
    plot_data = plot_data.melt(id_vars=["Feature"], var_name="Method")
    plot_data = plot_data.sort_values(by=["Method", "value"], ascending=False)
    plot_data = plot_data.groupby("Method").head(top_n)
    plot_data = plot_data.pivot(
        index="Feature", columns="Method", values="value"
    ).reset_index()
    plot_data = plot_data.fillna(0)

    methods = [d for d in list(plot_data.columns[1:]) if not pd.isna(d)]
    src = ColumnDataSource(plot_data)
    x_range = plot_data["Feature"].unique().tolist()
    viridis = get_viridis_pallette(len(methods))

    # Stacked bar chart
    p = figure(
        x_range=x_range,
        height=500,
        width=800,
        title="Importance of Features by Method",
        toolbar_location=None,
        tools="hover",
        tooltips=[
            ("Method", "$name"),
            ("Feature", "@Feature"),
            ("Importance", "@$name{0.000}"),
        ],
    )

    p.vbar_stack(
        methods,
        x="Feature",
        width=0.9,
        source=src,
        color=viridis,
        legend_label=[format_string(d) for d in methods],
    )

    p.y_range.start = 0
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.legend.location = "top_right"
    p.legend.orientation = "vertical"
    p.add_layout(p.legend[0], "right")
    p.xaxis.major_label_orientation = 1.1

    return p
