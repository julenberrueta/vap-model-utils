
# 📊 VAP Utils
*Utility functions for data processing, imputation, feature engineering, modeling, and visualization, tailored for Ventilator-Associated Pneumonia (VAP) research.*

---

## 📁 Project Structure

```
vap-model-utils/
│
├── docs/                           # App simulation: interactive ICU web app to visualize predictions
├── vap_utils/                      # Main package directory
│   ├── 01_PREPROCESSING.ipynb      # Preprocessing: imputation, missing analysis, categorical dummies, stats (-24h window)
│   ├── 02_BEST_CLASSIFIER.ipynb    # Benchmarking: scores for all horizons, models, and feature selectors
│   ├── 03_TRAIN_MODELS.ipynb       # Train CatBoost models (-1h, -24h, -48h) with selected features & hyperparameters
│   ├── 04_EXPLAINABILITY.ipynb     # Explainability: SHAP plots and calibration plots
│
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation (this file)
```

---

## 🛠 Notebooks Workflow

### **`01_PREPROCESSING.ipynb`**
- Imputation of missing values.  
- Identification of variables with >30% missingness.  
- Statistical analysis of the **-24h time window**.  
- Creation of dummy variables for categorical features.  

---

### **`02_BEST_CLASSIFIER.ipynb`**
- Compute all classification scores across:  
  - Different **time horizons**.  
  - Multiple **models**.  
  - Various **feature selection methods**.  
- Corresponds to **Section 2.5** of the article.  

---

### **`03_TRAIN_MODELS.ipynb`**
- Train **CatBoost models** at horizons **-1h, -24h, and -48h**.  
- Use the optimal number of features determined in `02_BEST_CLASSIFIER`.  
- Hyperparameter tuning for each model.  
- Display and compare performance results of all models.
- Corresponds to **Section 2.7** of the article. 

---

### **`04_EXPLAINABILITY.ipynb`**
- Generate and save **iterative imputer** file.
- Generate **SHAP plots** for interpretability.  
- Produce **calibration plots** to evaluate probability estimates.  

---

## 📊 `docs/` App Simulation
Contains all the necessary files to **visualize predictions** in a simulated environment, replicating the ICU web app used in production.  

---

## 📄 Configuration and Metadata

- **`requirements.txt`**  
  Lists all dependencies required to reproduce the pipeline.  

---

### ✨ Acknowledgments

- Developed by **Julen Berrueta Llona** 🧑‍💻  
- Built to streamline data processing, predictive modeling, and deployment for **Ventilator-Associated Pneumonia** research.  
