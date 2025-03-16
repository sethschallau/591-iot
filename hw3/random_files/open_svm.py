import pandas as pd
import numpy as np
import pickle
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

print("-------------open_svm------------------------")

files = ["closed_clean.csv", "closing_clean.csv", "open_clean.csv", "opening_clean.csv"]

def load_and_label_data(files):
    dataframes = []
    for file in files:
        df = pd.read_csv("raw_data/" + file)
        df["state"] = df["state"].map({
            "closed": 0, "open": 1,
            "closing": 0, "opening": 0 
        })
        dataframes.append(df)
    return pd.concat(dataframes, ignore_index=True)

df = load_and_label_data(files)

def create_chunks(df, chunk_size=6):
    X, y = [], []
    for i in range(len(df) - chunk_size + 1):
        chunk = df.iloc[i:i + chunk_size]
        features = chunk[["ax", "ay", "az", "gx", "gy", "gz"]].values.flatten()
        label = chunk["state"].values[-1]
        X.append(features)
        y.append(label)
    return np.array(X), np.array(y)

X, y = create_chunks(df, chunk_size=6)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

svm_pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC())
])

param_grid = {
    'svm__C': [0.1, 1, 10],  
    'svm__gamma': ['scale', 0.1, 1],  
    'svm__kernel': ['rbf']
}

grid_search = GridSearchCV(svm_pipeline, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_

y_pred = best_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("Best Parameters:", grid_search.best_params_)
print("\nOptimized Model Metrics:")
print(f"Accuracy: {accuracy:.2%}")
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print(f"F1 Score: {f1:.2%}")

with open("optimized_svm_model.pkl", "wb") as model_file:
    pickle.dump(best_model, model_file)
