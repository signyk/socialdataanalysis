import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import seaborn as sns
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from utils.make_data import get_data, clean_data, get_neighborhoods
from utils.const import FIRE_CALL_TYPES
from utils.plot_functions import make_bokeh_line_plot, make_map

dat_raw = get_data()
dat = clean_data(dat_raw)

dat.columns

dat = dat[dat["call_type"] == "Medical Incident"]
dat = dat.reset_index(drop=True)

# dat_filt = dat[
#     dat["neighborhood"].isin(
#         [
#             "Tenderloin",
#             "South of Market",
#             "Mission",
#             "Financial District/South Beach",
#             "Bayview Hunters Point",
#         ]
#     )
# ]
dat_filt = dat
# create bins for the hour of the day
bins = [-1, 6, 12, 18, 24]
labels = ["Night", "Morning", "Afternoon", "Evening"]
dat_filt["period_of_day"] = pd.cut(dat_filt["hour"], bins=bins, labels=labels)
dat_filt = dat_filt[dat_filt["call_date"].dt.year >= 2017]
dat_mini = dat_filt.sample(n=100000)
y = dat_mini["on_scene_time"]
X_dat = dat_mini[["neighborhood", "period_of_day"]]
X_dat = X_dat.reset_index(drop=True)


# X_dat = pd.get_dummies(X_dat, prefix_sep="_")

# le = preprocessing.LabelEncoder()
# le.fit(X_dat['neighborhood'].unique())
# X_dat['neigh_tr'] = le.transform(X_dat['neighborhood'])

# le.fit(X_dat['period_of_day'].unique())
# X_dat['period_of_day_tr'] = le.transform(X_dat['period_of_day'])

# X = X_dat[["neigh_tr", "period_of_day_tr"]]

Y = LabelEncoder().fit_transform(y)
X = X_dat
# X = StandardScaler().fit_transform(X)

##############

gsc = GridSearchCV(
    estimator=RandomForestRegressor(),
    param_grid={
        "max_depth": range(3, 10),
        "n_estimators": (10, 100, 299),
        "min_samples_split": [8, 10, 12],
        "min_samples_leaf": [3, 4, 5],
    },
    cv=3,
    scoring="neg_mean_squared_error",
    verbose=0,
    n_jobs=-1,
)

X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.30, random_state=101
)

grid_result = gsc.fit(X_train, y_train)
best_params = grid_result.best_params_

# rfr = RandomForestRegressor(max_depth=5, n_estimators=10, min_samples_split = 8, min_samples_leaf =5,random_state=0, verbose=False)
rfr = RandomForestRegressor(
    max_depth=best_params["max_depth"],
    n_estimators=best_params["n_estimators"],
    min_samples_split=best_params["min_samples_split"],
    min_samples_leaf=best_params["min_samples_leaf"],
    random_state=0,
    verbose=False,
)

print("Result of the grid search: ", best_params)

rfr.fit(X_train, y_train)
print("R^2 score for the train set: ", rfr.score(X_train, y_train))
print("R^2 score for the test set: ", rfr.score(X_test, y_test))

rfr.feature_importances_

############

from sklearn.decomposition import PCA

X_dat = pd.get_dummies(X_dat, prefix_sep="_")
Y = LabelEncoder().fit_transform(y)
X = X_dat
X = StandardScaler().fit_transform(X)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)
PCA_df = pd.DataFrame(data=X_pca, columns=["PC1", "PC2"])
PCA_df = pd.concat([PCA_df, dat_mini["on_scene_time"].reset_index(drop=True)], axis=1)
PCA_df["on_scene_time"] = LabelEncoder().fit_transform(PCA_df["on_scene_time"])
PCA_df.head()


pca = PCA(svd_solver="full")
X_pca = pca.fit_transform(X)
print(pca.explained_variance_)


#########################

X = dat_mini[["neighborhood", "period_of_day"]]
y = dat_mini["on_scene_time"]

# Encode categorical variables as dummy variables
X = pd.get_dummies(X, columns=["neighborhood", "period_of_day"])

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Instantiate LinearRegression model
model = LinearRegression()

# Fit model on training data
model.fit(X_train, y_train)

# Make predictions on testing data
y_pred = model.predict(X_test)

# Evaluate model performance
mse = mean_squared_error(y_test, y_pred)
r2 = model.score(X_test, y_test)

print("Mean squared error:", mse)
print("R-squared:", r2)

##########################

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm


# Fit OLS model
model = ols(
    "ContinuousVariable ~ Category1_Group1 + Category1_Group2 + Category2_Group1 + Category2_Group2",
    data=X.join(y),
).fit()

# Perform ANOVA
anova_results = anova_lm(model)

# Interpret the results
print(anova_results)
