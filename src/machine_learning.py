""" Importing packages """
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd

# Machine learning
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.metrics import mean_squared_error
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression

# Bokeh
from bokeh.plotting import show, figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, DatetimeTickFormatter
from bokeh.io import show, output_file

# Local
from utils.make_data import get_data, clean_data, get_neighborhoods, filter_data_years
from utils.const import FILTER_CALL_TYPES
from utils.plot_functions import (
    make_bokeh_line_plot,
    make_map,
    make_bokeh_tabs,
    make_cal_plot,
    plot_importance,
)
from utils.help_functions import get_viridis_pallette, format_string

""" Importing data """
dat_raw = get_data()
dat_all_years = clean_data(dat_raw)
dat_all_call_types = filter_data_years(dat_all_years, 2017, 2023)
dat = dat_all_call_types[dat_all_call_types["call_type"] == "Medical Incident"]

""" Machine Learning """
# Create a sample of the data to speed up the process
dat_mini = dat.sample(n=100000)
y = dat_mini["on_scene_time"]
X_dat = dat_mini[["neighborhood", "period_of_day"]]
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

""" Random Forest """
model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=1)
model.fit(X_train, y_train)

# Predict the on-scene time for the data
y_pred = model.predict(X_test)

# Calculate the mean squared error
mean_squared_error(y_test, y_pred)

# Get the feature importances
importances = model.feature_importances_

p = plot_importance(column_names, importances)
output_file("figs/feature_importance_random_forest.html")
show(p)

# Get the indices of the most important features
indices = importances.argsort()[-5:][::-1]

# Get the names of the most important features
names = [column_names[i] for i in indices]


""" Tree-based feature selection """
# Create an instance of ExtraTreesRegressor
et = ExtraTreesRegressor(n_estimators=100)

# Fit ExtraTreesRegressor on the training data
et.fit(X_train, y_train)

# Print the feature importances
print(et.feature_importances_)

p = plot_importance(column_names, et.feature_importances_)
output_file("figs/feature_importance_tree_based.html")
show(p)


""" Recursive feature elimination """
# Create an instance of linear regression
lr = LinearRegression()

# Create an instance of RFE
rfe = RFE(lr, n_features_to_select=5)

# Fit RFE on the training data
rfe.fit(X_train, y_train)

# Print the most important features
print(column_names[rfe.support_])
