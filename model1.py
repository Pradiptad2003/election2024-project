import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import uuid
import joblib
import os


# ================== 🔥 PREDICT FUNCTION ==================
def predict_seat(vote_percent):
    if not os.path.exists("mlp_model.pkl"):
        return "⚠️ Model not trained yet! Please upload dataset first."

    model = joblib.load("mlp_model.pkl")
    return model.predict([[vote_percent]])[0]


# ================== 🔥 TRAIN + TEST + GRAPH ==================
def run_mlp(path):

    # Load dataset
    df = pd.read_csv(path)

    X = df[['%Vote']].values
    y = df['Seat Share'].values

    # Split
    x_train, x_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train
    model = MLPRegressor(hidden_layer_sizes=(20,10), max_iter=1000, random_state=42)
    model.fit(x_train, y_train)

    # Save model
    joblib.dump(model, "mlp_model.pkl")

    # Predictions
    y_test_pred = model.predict(x_test)

    # 🔥 METRICS ADD (IMPORTANT)
    mse = mean_squared_error(y_test, y_test_pred)
    r2 = r2_score(y_test, y_test_pred)

    # 🔥 Smooth curve
    x_range = np.linspace(X.min(), X.max(), 100).reshape(-1,1)
    y_range_pred = model.predict(x_range)

    # Plot
    plt.figure(figsize=(8,5))

    # Actual vs Predicted (Test)
    plt.scatter(x_test, y_test, color='green', label='Actual (Test Data)')
    plt.scatter(x_test, y_test_pred, color='red', label='Predicted (Model Output)')

    # Regression Curve
    plt.plot(x_range, y_range_pred, color='black', label='MLP Regression Curve')

    # 🔥 ERROR LINE (NEW ADD)
    for i in range(len(x_test)):
        plt.plot([x_test[i], x_test[i]],
                 [y_test[i], y_test_pred[i]],
                 linestyle='dotted', color='gray')

    # Labels
    plt.xlabel("Vote %")
    plt.ylabel("Seat Share")
    plt.title("MLP Regression on Test Data (Actual vs Predicted)")

    # 🔥 METRICS TEXT (TOP LEFT)
    plt.text(0.05, 0.95,
             f'R² Score: {r2:.2f}\nMSE: {mse:.2f}',
             transform=plt.gca().transAxes,
             verticalalignment='top',
             bbox=dict(facecolor='white', alpha=0.7))

    plt.legend()
    plt.grid(True)

    # Save graph
    graph_path = f"static/{uuid.uuid4().hex}.png"
    plt.savefig(graph_path)
    plt.close()

    return "Model trained, tested & evaluated", graph_path