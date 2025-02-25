
# 📊 VAP Utils
*Utility functions for data processing, imputation, feature engineering, modeling, and visualization, tailored for Ventilator-Associated Pneumonia (VAP) research.*

---

## 📁 Project Structure

```
vap-model-utils/
│
├── vap_utils/                      # Main package directory
│   ├── __init__.py                 # Initializes the package
│   ├── data_processing.py          # Functions for data preprocessing and time window expansion
│   ├── imputation.py               # Functions for missing value imputation and outlier removal
│   ├── feature_engineering.py      # Functions for feature extraction and transformation
│   ├── model_utils.py              # Functions for model training, hyperparameter tuning, and evaluation
│   └── visualization.py            # Functions for data and model visualization
│
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation (this file)
```

---

## 🛠 Contents and Purpose

### 1. Main Package (`vap_utils/`)
- **`data_processing.py`**  
  Functions for preprocessing time-series data, such as expanding data into rolling time windows for patient monitoring.

- **`imputation.py`**  
  Handles missing data imputation and outlier removal using robust methods.

- **`feature_engineering.py`**  
  Functions to extract and transform features from raw data, enabling better model performance.

- **`model_utils.py`**  
  Tools for training models, performing hyperparameter tuning (e.g., Optuna), and handling imbalanced datasets.

- **`visualization.py`**  
  Functions for visualizing data, patient timelines, probabilities, and key events using libraries like Plotly.

---

## 📄 Configuration and Metadata

- **`requirements.txt`**  
  Lists the project's dependencies.

---

### ✨ Acknowledgments

- Developed by **Julen Berrueta Llona** 🧑‍💻  
- Built to streamline data processing and modeling for **Ventilator-Associated Pneumonia** research.
