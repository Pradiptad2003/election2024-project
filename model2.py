import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import numpy as np
import uuid

# 🔥 Sentiment Score Function (Paper based)
def calculate_sentiment_score(pos, neg, neu):
    total = pos + neg + neu
    if total == 0:
        return 0

    return (pos*1 + neg*(-1) + neu*0.2) / total


def run_sentiment(path):
    df = pd.read_csv(path)

    S = df['Sentiment Score']
    V = df['Vote %']

    # Regression
    m, b = np.polyfit(S, V, 1)
    pred = m*S + b

    # Correlation
    r, p = pearsonr(S, V)

    # Graph
    plt.figure()
    plt.scatter(S, V)
    plt.plot(S, pred)
    plt.xlabel("Sentiment Score")
    plt.ylabel("Vote %")

    graph_path = f"static/{uuid.uuid4().hex}.png"
    plt.savefig(graph_path)
    plt.close()

    result = f"Correlation: {round(r,3)}, p-value: {round(p,5)}"

    return result, graph_path