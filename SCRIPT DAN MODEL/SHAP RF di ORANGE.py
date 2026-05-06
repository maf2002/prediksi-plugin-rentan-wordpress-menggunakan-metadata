import shap
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier

# =========================
# LOAD DATA
# =========================
data = in_data

X = data.X
y = data.Y

feature_names = [var.name for var in data.domain.attributes]

# =========================
# TRAIN MODEL
# =========================
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# =========================
# SHAP
# =========================
explainer = shap.TreeExplainer(rf_model)
shap_values = explainer.shap_values(X)

# =========================
# HANDLE SHAPE (FIX ERROR)
# =========================
if isinstance(shap_values, list):
    shap_plot = shap_values[1]   # class 1 (rentan)
else:
    shap_plot = shap_values[:, :, 1]  # ambil class 1 dari array 3D

# =========================
# PLOT
# =========================
print("=== SHAP Summary Plot (Random Forest) ===")
shap.summary_plot(shap_plot, X, feature_names=feature_names)

print("=== SHAP Bar Plot ===")
shap.summary_plot(shap_plot, X, feature_names=feature_names, plot_type="bar")