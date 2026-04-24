# ----------------------------------------------------------
# train_dl.py
# Deep Learning model for RC circuit prediction (Jupyter-safe)
# ----------------------------------------------------------

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import os

# ----------------------------------------------------------
# Model Architecture
# ----------------------------------------------------------

class RCNet(nn.Module):
    def __init__(self, input_dim=3, hidden_dim=128, output_dim=1):
        """
        Fully connected NN for predicting RC circuit Vout
        """
        super(RCNet, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        return self.net(x)


# ----------------------------------------------------------
# Training Function
# ----------------------------------------------------------

def train_deep_learning(
        data_csv="spice_dataset.csv", 
        model_out="model_dl.pt",
        epochs=30, 
        batch_size=32, 
        lr=1e-3
    ):
    """
    Train RCNet using SPICE CSV dataset.
    Works inside Jupyter.
    """

    if not os.path.exists(data_csv):
        raise FileNotFoundError(f"Dataset {data_csv} not found!")

    df = pd.read_csv(data_csv)

    # Features: R, C, Vin
    X = df[["R", "C", "Vin"]].values.astype(np.float32)
    y = df["Vout"].values.astype(np.float32).reshape(-1, 1)

    X_tensor = torch.tensor(X)
    y_tensor = torch.tensor(y)

    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = RCNet()
    loss_fn = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    print("🚀 Training deep learning model...")

    for epoch in range(epochs):
        total_loss = 0.0

        for X_batch, y_batch in loader:
            optimizer.zero_grad()
            pred = model(X_batch)
            loss = loss_fn(pred, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"[Epoch {epoch+1}/{epochs}] Loss = {total_loss:.6f}")

    torch.save(model.state_dict(), model_out)
    print(f"✅ Saved DL model to: {model_out}")

    return model


# ----------------------------------------------------------
# Allow CLI usage
# ----------------------------------------------------------

if __name__ == "__main__":
    train_deep_learning()
