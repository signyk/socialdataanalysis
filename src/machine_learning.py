"""" Importing packages """
import random
import pandas as pd
import numpy as np
from bokeh.io import show, output_file

# Machine learning
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Local
from utils.make_data import (
    get_data,
    clean_data,
    filter_data_years,
)
from utils.plot_functions import plot_importance


""" Importing data """
dat_raw = get_data()
dat_all_years = clean_data(dat_raw)
dat = filter_data_years(dat_all_years, 2017, 2023)

""" Prepare the data """
# Create the target variable and the features
ml_dat = dat.copy()
ml_dat["Year"] = ml_dat["call_date"].dt.year
y = ml_dat["response_time"].reset_index(drop=True)
X_dat = ml_dat[["neighborhood", "period_of_day", "Year"]]
X_dat = X_dat.reset_index(drop=True)

# Handle categorical variables
X_dat = pd.get_dummies(X_dat, columns=["neighborhood", "period_of_day"])
column_names = X_dat.columns
# Scale the data
scaler = StandardScaler()
X_dat = scaler.fit_transform(X_dat)

""" Random Forest """
random.seed(123)
# Use bootstrapping
n_iterations = 10
sample_size = 100000
importances_array = np.zeros((X_dat.shape[1], n_iterations))

for i in range(n_iterations):
    # Take a sample of the data
    sample = random.sample(range(len(X_dat)), sample_size)
    X_dat_sample = X_dat[sample, :]
    # Get the corresponding rows in the target variable
    y_sample = y[sample]

    # Create the model
    model = RandomForestRegressor(n_estimators=100, max_depth=5)
    model.fit(X_dat_sample, y_sample)

    # Get the feature importances
    importances_rf = model.feature_importances_

    # Add the importances to the array
    importances_array[:, i] = model.feature_importances_le = (
        "Feature importances according to Random Forest",
    )

# Plot the feature importances
# Calculate the mean of the importances
importances_rf = np.mean(importances_array, axis=1)

# Get the 10 most important features
indices = np.argsort(importances_rf)[::-1]
indices = indices[:10]

p = plot_importance(
    column_names=column_names[indices],
    importances=importances_rf[indices],
    title="Feature importances according to Random Forest",
)

output_file("figs/feature_importance.html")
show(p)
