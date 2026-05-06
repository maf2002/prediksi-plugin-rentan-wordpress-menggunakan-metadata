import shap
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression

# =========================
# LOAD DATA DARI ORANGE
# =========================
data = in_data

X = data.X
y = data.Y

feature_names = [var.name for var in data.domain.attributes]

# =========================
# TRAIN MODEL
# =========================
lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X, y)

# =========================
# SHAP ANALYSIS
# =========================
explainer = shap.LinearExplainer(lr_model, X)
shap_values = explainer.shap_values(X)

# =========================
# HANDLE OUTPUT
# =========================
# Beberapa versi SHAP:
# - langsung array (n_sample, n_feature)
# - atau list [class_0, class_1]

if isinstance(shap_values, list):
    shap_plot = shap_values[1]   # ambil kelas rentan
else:
    shap_plot = shap_values

# =========================
# VISUALISASI
# =========================
print("=== SHAP Summary Plot (Logistic Regression) ===")
shap.summary_plot(shap_plot, X, feature_names=feature_names)

print("=== SHAP Bar Plot ===")
shap.summary_plot(shap_plot, X, feature_names=feature_names, plot_type="bar")