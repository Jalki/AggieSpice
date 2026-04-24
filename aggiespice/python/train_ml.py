# ----------------------------------------------------------
# train_ml.py
# Traditional ML regression model for RC circuit
# ----------------------------------------------------------

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def train_machine_learning(
        data_csv="spice_dataset.csv",
        model_out="model_ml.pkl"
    ):
    """
    Train a Random Forest on SPICE data.
    """

    if not os.path.exists(data_csv):
        raise FileNotFoundError(f"{data_csv} missing.")

    df = pd.read_csv(data_csv)

    X = df[["R", "C", "Vin"]].values
    y = df["Vout"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=300)
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)

    print(f"ML Model R^2 Score: {score:.4f}")

    joblib.dump((model, scaler), model_out)
    print(f"Saved ML model to: {model_out}")

    return model, scaler


if __name__ == "__main__":
    train_machine_learning()
