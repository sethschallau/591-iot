import json
import numpy as np
from collections import deque
import pickle

buffer = deque(maxlen=6)

def load_classifier():
    with open("svm_model.pkl", "rb") as f:
        return pickle.load(f)

classifier = load_classifier()

def classify_chunk(chunk):
    features = np.array(chunk).flatten().reshape(1,-1)
    prediction = classifier.predict(features)
    majority_vote = np.round(np.mean(prediction))
    return "stable" if majority_vote == 0 else "moving"

# Simulated sensor data (replace with real test data)
test_data = [
    {"ax": 0.1, "ay": 0.2, "az": 0.9, "gx": -3.0, "gy": -0.5, "gz": 0.7},
    {"ax": 0.1, "ay": 0.2, "az": 0.9, "gx": -3.0, "gy": -0.5, "gz": 0.7},
    {"ax": 0.1, "ay": 0.2, "az": 0.9, "gx": -3.0, "gy": -0.5, "gz": 0.7},
    {"ax": 0.1, "ay": 0.2, "az": 0.9, "gx": -3.0, "gy": -0.5, "gz": 0.7},
    {"ax": 0.1, "ay": 0.2, "az": 0.9, "gx": -3.0, "gy": -0.5, "gz": 0.7},
    {"ax": 0.1, "ay": 0.2, "az": 0.9, "gx": -3.0, "gy": -0.5, "gz": 0.7},
]

for data in test_data:
    buffer.append([data["ax"], data["ay"], data["az"], data["gx"], data["gy"], data["gz"]])
    if len(buffer) == 6:
        result = classify_chunk(list(buffer))
        print(f"Chunk Classified as: {result}")
