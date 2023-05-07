""" Importing packages """
import datetime as dt
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
import folium
import plotly.express as px
import matplotlib.pyplot as plt

from utils.make_data import get_data, clean_data, get_on_scene_map
from utils.help_functions import get_viridis_pallette, format_string

""" Importing data """
dat_raw = get_data()
dat = clean_data(dat_raw)

# print the names of the columns of the data
print(dat.columns)


# Splittad on_scene_time
split_time_data = dat.copy()
split_time_data["intake_time"] = (
    split_time_data["entry_dttm"] - split_time_data["received_dttm"]
).dt.total_seconds() / 60
split_time_data["queue_time"] = (
    split_time_data["dispatch_dttm"] - split_time_data["entry_dttm"]
).dt.total_seconds() / 60
split_time_data["travel_time"] = (
    split_time_data["on_scene_dttm"] - split_time_data["dispatch_dttm"]
).dt.total_seconds() / 60
# ath hoppa yfir response_dttm, veit ekki nkl hvar thad kemur inn
split_time_data["Year"] = split_time_data["received_dttm"].dt.year.astype(str)

print(split_time_data.columns)

long = split_time_data.melt(
    id_vars="Year",
    value_vars=["intake_time", "queue_time", "travel_time"],
    var_name="Time",
    value_name="minutes",
)

res = long.groupby(["Time", "Year"])["minutes"].mean().reset_index(name="mean")

processed_dat = res.pivot(index="Year", columns="Time", values="mean").reset_index()

from bokeh.models import ColumnDataSource, FactorRange, Legend
from bokeh.plotting import figure, show

output_file("figs/split_time.html")
descripts = [d for d in list(long["Time"].unique()) if not pd.isna(d)]
src = ColumnDataSource(processed_dat)
x_range = processed_dat["Year"].unique().tolist()
viridis = get_viridis_pallette(len(descripts))

# Stacked bar chart
p2 = figure(
    x_range=x_range,
    height=500,
    width=800,
    title="Average on-scene time per year",
    toolbar_location=None,
    tools="hover",
    tooltips=[
        ("Type", "$name"),
        ("Year", "@Year"),
        ("Time", "@$name"),
    ],
)

p2.vbar_stack(
    descripts,
    x="Year",
    width=0.9,
    source=src,
    color=viridis,
    legend_label=[format_string(d) for d in descripts],
)

p2.y_range.start = 0
p2.xgrid.grid_line_color = None
p2.axis.minor_tick_line_color = None
p2.outline_line_color = None
p2.legend.location = "top_right"
p2.legend.orientation = "vertical"
p2.add_layout(p2.legend[0], "right")

show(p2)


## AÐRAR VANGAVELTUR

get_on_scene_map(dat)
dat = dat.loc[dat["on_scene_time"] >= 0]
dat = dat.loc[dat["on_scene_time"] < 1440]
battalions = dat["battalion"].unique()


# We look at resolution in each district
av = dat.groupby("battalion")["on_scene_time"].mean()
av.plot.bar()
plt.show()

from folium import plugins
from folium.plugins import HeatMap

# Heatmaps for sex offences
sanfran = [37.773972, -122.431297]
battalion = dat[dat["battalion"] == "B12"]
battalion = battalion.dropna()
heatdata = battalion[["longitude", "latitude"]].values.tolist()
heatm = folium.Map(sanfran, zoom_start=13, tiles="OpenStreetMap", control_scale=True)
# Plot it on the map
hm = HeatMap(
    heatdata,
    gradient={0.1: "blue", 0.3: "lime", 0.5: "yellow", 0.7: "orange", 1: "red"},
    min_opacity=0.7,
    max_opacity=0.9,
    radius=10,
    use_local_extrema=False,
)  # .add_to(base_map)
heatm.add_child(hm)

# Display the map
heatm.save("b12.html")
save(heatm)

from scipy import stats
import statsmodels.stats.multicomp as mc

comp1 = mc.MultiComparison(dat["on_scene_time"], dat["neighborhood"])
tbl, a1, a2 = comp1.allpairtest(stats.ttest_ind, method="bonf")


from bokeh.models import ColumnDataSource, FactorRange, Legend, HoverTool
from bokeh.plotting import figure, show
from bokeh.palettes import YlGnBu, Spectral, Bokeh
from bokeh.io import output_file, show

fire_call_types = set(
    [
        "Outside Fire",
        "Structure Fire",
        "Vehicle Fire",
        "Explosion",
        "Train / Rail Fire",
        "Structure Fire / Smoke in Building",
        "Electrical Hazard",
        "Confined Space / Structure Collapse",
        "Medical Incident",
        "Traffic Collision",
        "Elevator / Escalator Rescue",
    ]
)
dat_fire = dat[dat["call_type"].isin(fire_call_types)]
dat_fire.columns
dat_fire = dat_fire[dat_fire["neighborhood"].notna()]
dat_fire["Year"] = dat_fire["received_dttm"].dt.year

res = (
    dat_fire.groupby(["neighborhood", "Year"])["on_scene_time"]
    .mean()
    .reset_index(name="mean")
)
processed_dat = res.pivot(
    index="Year", columns="neighborhood", values="mean"
).reset_index()

# pallette = Spectral[11]
# output_file("bokeh_inter.html")
descripts = [
    "Hayes Valley",
    "South of Market",
    "Mission",
    "Russian Hill",
    "Financial District/South Beach",
    "Golden Gate Park",
    "Tenderloin",
    "Seacliff",
    "Outer Mission",
    "Bernal Heights",
    "Potrero Hill",
    "Marina",
    "Nob Hill",
    "Lakeshore",
    "Presidio Heights",
    "Lone Mountain/USF",
    "Haight Ashbury",
    "West of Twin Peaks",
    "Noe Valley",
    "Bayview Hunters Point",
    "Sunset/Parkside",
    "Chinatown",
    "Pacific Heights",
    "Portola",
    "Mission Bay",
    "Western Addition",
    "North Beach",
    "Inner Sunset",
    "Oceanview/Merced/Ingleside",
    "Twin Peaks",
    "Castro/Upper Market",
    "Excelsior",
    "Japantown",
    "Inner Richmond",
    "Treasure Island",
    "Visitacion Valley",
    "Presidio",
    "Outer Richmond",
    "McLaren Park",
    "Glen Park",
    "Lincoln Park",
]

descripts = [
    "Bayview Hunters Point",
    "Bernal Heights",
    "Castro/Upper Market",
    "Chinatown",
    "Excelsior",
    "Financial District/South Beach",
    "Glen Park",
    "Golden Gate Park",
    "Haight Ashbury",
    "Hayes Valley",
    "Inner Richmond",
    "Inner Sunset",
    "Japantown",
    "Lakeshore",
    "Lincoln Park",
    "Lone Mountain/USF",
    "Marina",
    "McLaren Park",
    "Mission",
    "Mission Bay",
    "Nob Hill",
    "Noe Valley",
    "North Beach",
    "Oceanview/Merced/Ingleside",
    "Outer Mission",
    "Outer Richmond",
    "Pacific Heights",
    "Portola",
    "Potrero Hill",
    "Presidio",
    "Presidio Heights",
    "Russian Hill",
    "Seacliff",
    "South of Market",
    "Sunset/Parkside",
    "Tenderloin",
    "Treasure Island",
    "Twin Peaks",
    "Visitacion Valley",
    "West of Twin Peaks",
    "Western Addition",
]
processed_dat.columns

src = ColumnDataSource(processed_dat)
years = [str(i) for i in range(2012, 2022)]
p = figure(
    x_range=years,
    height=500,
    width=800,
    title="Average response time by neighborhood by years",
    toolbar_location=None,
    tools="hover",
)

items = []  ### for the custom legend
bar = {}  # to store vbars
### here we will do a for loop:
for indx, i in enumerate(descripts):
    ### we will create a vbar for each focuscrime
    bar[i] = p.line(
        x="Year", y=i, source=src, alpha=0.9, muted_alpha=0.1, width=0.9, line_width=2
    )
    items.append((i, [bar[i]]))
    bar[i].visible = True if i == list(descripts)[0] else False
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
        ("Year", "@Year"),
        ("Value", "$y{0}"),
    ]
    # hover.mode = 'mouse'

legend = Legend(items=items, location=(0, 10))  ## figure where to add it
p.add_layout(legend, "left")
p.legend.click_policy = (
    "hide"  ### assigns the click policy (you can try to use ''hide')
)
p.xaxis.axis_label = "Year"
p.yaxis.axis_label = "Average response time"
p.y_range.only_visible = True
p.y_range.start = 0
p.sizing_mode = "scale_width"

# bokeh_deepnote_show(p) #displays your plot
show(p)

# Skoda priority
medical = dat[dat["call_type"] == "Medical Incident"]
bla = medical.groupby("original_priority")["neighborhood"].value_counts()
medical.groupby("original_priority")["neighborhood"].nunique()
medical.groupby("call_type_group")["on_scene_time"].mean()

dat.groupby("battalion")["on_scene_time"].mean()
dat["call_type"].value_counts()
medical["priority"].value_counts()
medical["final_priority"].value_counts()


## Look into april 2022
caldat = dat.copy()
caldat = caldat[caldat["call_type"].isin(["Medical Incident"])]
caldat = caldat[caldat["received_dttm"].dt.year == 2022]
caldat = caldat[caldat["received_dttm"].dt.month == 4]
caldat.sort_values(by="received_dttm", inplace=True)
print(caldat.columns)
aprilfools = caldat[
    caldat["received_dttm"].dt.date == dt.date(year=2022, month=4, day=1)
]
april17th = caldat[
    caldat["received_dttm"].dt.date == dt.date(year=2022, month=4, day=17)
]
april2nd = caldat[caldat["received_dttm"].dt.date == dt.date(year=2022, month=4, day=2)]
# Select the relevant columns ("received_dttm" and column_name)
caldat = caldat[["received_dttm", "on_scene_time"]]
# Set the index to be the date
caldat = caldat.set_index("received_dttm")

alldat = dat.copy()
april2nd = dat_raw[
    dat_raw["Received DtTm"].dt.date == dt.date(year=2022, month=4, day=2)
]
