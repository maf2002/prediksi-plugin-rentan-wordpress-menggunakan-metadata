import numpy as np
import shap
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.naive_bayes import GaussianNB

# =========================
# LOAD DATA DARI ORANGE
# =========================
data = in_data

X = data.X
y = data.Y

feature_names = [attr.name for attr in data.domain.attributes]

print("Jumlah fitur:", len(feature_names))

# =========================
# TRAIN MODEL
# =========================
model = GaussianNB()
model.fit(X, y)

# =========================
# SAMPLING
# =========================
background = shap.sample(X, 200)
test_sample = shap.sample(X, 300)

# =========================
# EXPLAINER
# =========================
explainer = shap.KernelExplainer(
    model.predict_proba,
    background
)

shap_values = explainer.shap_values(test_sample)

# =========================
# HANDLE OUTPUT CLASS
# =========================
if isinstance(shap_values, list):
    shap_values_class1 = shap_values[1]   # kelas rentan
else:
    shap_values_class1 = shap_values[:, :, 1]

print("Shape SHAP:", shap_values_class1.shape)
print("Shape data:", test_sample.shape)

# =========================
# HITUNG AVERAGE IMPACT
# =========================
mean_abs_shap = np.abs(shap_values_class1).mean(axis=0)

importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Mean |SHAP Value|": mean_abs_shap
}).sort_values(by="Mean |SHAP Value|", ascending=False)

print("\n=== Feature Importance (Mean |SHAP|) ===")
print(importance_df)

# =========================
# VISUALISASI
# =========================
print("\n=== SHAP Summary Plot ===")
shap.summary_plot(
    shap_values_class1,
    test_sample,
    feature_names=feature_names,
    max_display=len(feature_names)
)

print("\n=== SHAP Bar Plot (Average Impact) ===")
shap.summary_plot(
    shap_values_class1,
    test_sample,
    feature_names=feature_names,
    plot_type="bar",
    max_display=len(feature_names)
)