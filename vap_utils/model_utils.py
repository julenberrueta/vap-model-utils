"""
-----------------------------------------------------
Module: model_utils.py
Description: Functions for model training, hyperparameter tuning, and class balancing.
Author: Julen Berrueta Llona
Created: 2024-10-27
-----------------------------------------------------
"""

def downsampling(X_train, y_train, majority_proportion=1.0):
    """
    Performs downsampling on the majority class to balance the dataset.

    Args:
    - X_train (numpy array): Feature matrix of the training data.
    - y_train (numpy array): Label array corresponding to the training data.
    - majority_proportion (float, optional): The ratio of majority class samples relative to the minority class.
        - A value of 1 results in equal numbers of positive and negative samples.
        - A value of 2 means the majority class has twice as many samples as the minority class.
        - Default is 1.0 (balanced dataset).

    Returns:
    - tuple: Downsampled feature matrix and label array.

    Example:
    --------
    >>> X_train_balanced, y_train_balanced = downsampling(X_train, y_train, majority_proportion=1.5)
    """

    # Separate minority and majority class samples
    X_train_minority = X_train[y_train == 1]  # Minority class (positive cases)
    X_train_majority = X_train[y_train != 1]  # Majority class (negative cases)
    y_train_majority = y_train[y_train != 1]  # Labels for majority class

    # Calculate the desired number of majority class samples after downsampling
    desired_majority_samples = int(len(X_train_minority) * majority_proportion)

    # Downsample the majority class to match the desired proportion
    X_train_majority_downsampled, y_train_majority_downsampled = resample(
        X_train_majority, y_train_majority,
        replace=False,  # No replacement to ensure unique samples
        n_samples=desired_majority_samples,  # Number of samples after downsampling
        random_state=42  # For reproducibility
    )

    # Combine the downsampled majority class with the minority class
    X_train_balanced = np.vstack((X_train_minority, X_train_majority_downsampled))
    y_train_balanced = np.hstack((np.ones(len(X_train_minority)), y_train_majority_downsampled))

    return X_train_balanced, y_train_balanced

def objective(trial):
    """
    Objective function for Optuna hyperparameter optimization of an XGBoost classifier.

    Args:
    - trial (optuna.trial.Trial): A trial object used by Optuna to suggest hyperparameters.

    Returns:
    - float: The mean ROC AUC score from cross-validation, which Optuna will aim to maximize.

    Hyperparameters tuned:
    - max_depth: Maximum depth of each tree (3 to 7).
    - n_estimators: Number of trees in the ensemble (100 to 500, in steps of 50).
    - learning_rate: Learning rate for boosting (0.01 to 0.3).
    - subsample: Subsample ratio for training each tree (0.7 to 1.0, in steps of 0.1).
    - colsample_bytree: Subsample ratio of columns for each tree (0.7 to 1.0, in steps of 0.1).

    Example:
    --------
    >>> study = optuna.create_study(direction='maximize')
    >>> study.optimize(objective, n_trials=50)
    """

    # Define the hyperparameter search space using Optuna's suggest methods
    param_space = {
        'max_depth': trial.suggest_int('max_depth', 3, 7),  # Control tree complexity
        'n_estimators': trial.suggest_int('n_estimators', 100, 500, step=50),  # Number of boosting rounds
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),  # Step size shrinkage
        'subsample': trial.suggest_float('subsample', 0.7, 1.0, step=0.1),  # Row subsampling to reduce overfitting
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.7, 1.0, step=0.1),  # Feature subsampling
    }

    # Define a stratified 3-fold cross-validation to maintain class balance in each fold
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    # Create the XGBoost classifier with the suggested hyperparameters
    model = XGBClassifier(**param_space, eval_metric="logloss", random_state=42)

    # Perform cross-validation and calculate ROC AUC score for each fold
    scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='roc_auc', n_jobs=-1)

    # Return the mean ROC AUC score to be maximized by Optuna
    return scores.mean()
