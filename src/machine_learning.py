""" Importing packages """
import pandas as pd
import matplotlib.pyplot as plt

# Machine learning
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.metrics import mean_squared_error
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression

# Bokeh
from bokeh.plotting import show, figure
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, HoverTool

# Local
from utils.make_data import get_data, clean_data, filter_data_years
from utils.plot_functions import plot_importance, plot_importance2
from utils.help_functions import get_viridis_pallette

""" Importing data """
dat_raw = get_data()
dat_all_years = clean_data(dat_raw)
dat_all_call_types = filter_data_years(dat_all_years, 2017, 2023)
dat = dat_all_call_types[dat_all_call_types["call_type"] == "Medical Incident"]

""" Machine Learning """
# Create a sample of the data to speed up the process
dat_mini = dat.sample(n=100000)
# Create the target variable and the features
dat_mini["Year"] = dat_mini["call_date"].dt.year
y = dat_mini["on_scene_time"]
X_dat = dat_mini[["neighborhood", "period_of_day", "Year"]]
X_dat = X_dat.reset_index(drop=True)

# Handle categorical variables
X_dat = pd.get_dummies(X_dat, columns=["neighborhood", "period_of_day"])
column_names = X_dat.columns
# Scale the data
scaler = StandardScaler()
X_dat = scaler.fit_transform(X_dat)
# Create traning and test data
y_train, y_test, X_train, X_test = train_test_split(
    y, X_dat, test_size=0.2, random_state=1
)

# Prepare a dataframe for the feature importances
feature_importances = pd.DataFrame(
    index=column_names, columns=["Random Forest", "Tree-based", "Recursive"]
)

""" Random Forest """
model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=1)
model.fit(X_train, y_train)

# Predict the on-scene time for the data
y_pred = model.predict(X_test)

# Calculate the mean squared error
mean_squared_error(y_test, y_pred)

# Get the feature importances
importances_rf = model.feature_importances_

# Get the 10 most important features
indices_rf = importances_rf.argsort()[-10:][::-1]

# Add importances to the dataframe
feature_importances["Random Forest"] = importances_rf

""" Tree-based feature selection """
# Create an instance of ExtraTreesRegressor
et = ExtraTreesRegressor(n_estimators=100)

# Fit ExtraTreesRegressor on the training data
et.fit(X_dat, y)

# Get the feature importances
importances_et = et.feature_importances_

# Select the 10 most important features
indices_et = importances_et.argsort()[-10:][::-1]

# Add importances to the dataframe
feature_importances["Tree-based"] = importances_et

""" Recursive feature elimination """
# Create an instance of linear regression
lr = LinearRegression()

# Create an instance of RFE
rfe = RFE(lr, n_features_to_select=10)

# Fit RFE on the training data
rfe.fit(X_dat, y)

# Print the most important features
print(column_names[rfe.support_])

# Get the feature importances
importances_rfe = rfe.ranking_

# Get the 10 most important features
indices_rfe = importances_rfe.argsort()[:10]


""" Summary """

# Plot the feature importances
plot_importance2(feature_importances, 10)

# Data frame the the top 10 features according to different methods
top_10_features = pd.DataFrame(
    {
        "Random Forest": column_names[indices_rf],
        "Tree-based feature selection": column_names[indices_et],
        "Recursive feature elimination": column_names[indices_rfe],
        "Importance": [i for i in range(10, 0, -1)],
    }
)

# Transform the data frame to long format
top_10_features_long = pd.melt(
    top_10_features, id_vars=["Importance"], var_name="Method", value_name="Feature"
)

processed_dat = top_10_features_long.pivot(
    index="Feature", columns="Method", values="Importance"
).reset_index()
processed_dat = processed_dat.fillna(0)

src = ColumnDataSource(processed_dat)

# Create a figure
p = figure(
    x_range=top_10_features_long["Feature"].unique(),
    height=500,
    width=800,
    title="Top 10 features",
    toolbar_location=None,
    tools="hover",
    tooltips=[
        ("Method", "$name"),
        ("Feature", "@Feature"),
        ("Importance", "@$name"),
    ],
)

# Add stacked bars to the figure for each method
p.vbar_stack(
    top_10_features_long["Method"].unique(),
    x="Feature",
    width=0.9,
    source=src,
    color=get_viridis_pallette(3),
    legend_label=[
        "Random Forest",
        "Tree-based feature selection",
        "Recursive feature elimination",
    ],
)

p.y_range.start = 0
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.location = "top_right"
p.xaxis.major_label_orientation = 1.2

show(p)
