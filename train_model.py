import pandas as pd
from sklearn.neural_network import MLPRegressor
import joblib

df = pd.read_csv("data/sample_model1.csv")

X = df[['%Vote']]
y = df['Seat Share']

model = MLPRegressor(hidden_layer_sizes=(20,10), max_iter=1000)
model.fit(X, y)

joblib.dump(model, "mlp_model.pkl")

print("✅ Model trained & saved")