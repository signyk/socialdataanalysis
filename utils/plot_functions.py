""" Importing packages """
import pandas as pd

# Bokeh
from bokeh.models import ColumnDataSource, Legend
from bokeh.plotting import figure
from bokeh.io import output_file

# Local
from utils.help_functions import get_viridis_pallette
from utils.const import FIRE_CALL_TYPES


def make_bokeh_line_plot(
    dat: pd.DataFrame,
    filename: str = "bokeh1.html",
    filter_call_types: list = FIRE_CALL_TYPES,
    color_var: str = "neighborhood",
    x_var: str = "Year",
    x_range: tuple = (2012, 2022),
):
    full_path = "figs/" + filename
    output_file(full_path)
    dat_fire = dat[dat["call_type"].isin(filter_call_types)]
    dat_fire = dat_fire[dat_fire[color_var].notna()]
    dat_fire["x_var"] = dat_fire[x_var]

    res = (
        dat_fire.groupby([color_var, x_var])["on_scene_time"]
        .mean()
        .reset_index(name="mean")
    )
    processed_dat = res.pivot(
        index=x_var, columns=color_var, values="mean"
    ).reset_index()

    descripts = [d for d in list(dat_fire[color_var].unique()) if not pd.isna(d)]
    src = ColumnDataSource(processed_dat)
    viridis = get_viridis_pallette(len(descripts))
    p = figure(
        # x_range=years,
        x_range=x_range,
        height=500,
        width=800,
        title="Average response time",
        toolbar_location=None,
        tools="hover",
        tooltips=[
            (color_var, "$name"),
            (x_var, "@x_var"),
            ("Average response time", "@$name"),
        ],
    )

    items = []  # for the custom legend
    lines = {}  # to store the lines

    for indx, i in enumerate(descripts):
        ### Create a line for each district
        lines[i] = p.line(
            x=x_var,
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
    p.yaxis.axis_label = "Average response time"
    p.y_range.only_visible = True
    p.y_range.start = 0
    p.sizing_mode = "scale_width"

    return p
