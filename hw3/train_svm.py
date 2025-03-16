import pandas as pd
import numpy as np
import pickle
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

files = ["closed_clean.csv", "closing_clean.csv", "open_clean.csv", "opening_clean.csv"]

def load_and_label_data(files):
    dataframes = []
    for file in files:
        df = pd.read_csv("raw_data/" + file)
        df["state"] = df["state"].map({
            "closed": 0, "open": 0,
            "closing": 1, "opening": 1 
        })
        
        dataframes.append(df)
    
    return pd.concat(dataframes, ignore_index=True)

df = load_and_label_data(files)

def create_chunks(df, chunk_size=12):
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
    ("svm", SVC(kernel="rbf", C=1.0, gamma="scale"))
])

cv_results_2 = cross_validate(svm_pipeline, X_train, y_train, cv=2, scoring=['accuracy', 'precision', 'recall', 'f1'])
cv_results_3 = cross_validate(svm_pipeline, X_train, y_train, cv=3, scoring=['accuracy', 'precision', 'recall', 'f1'])

svm_pipeline.fit(X_train, y_train)

y_pred = svm_pipeline.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\nCross-Validation Results (2-Fold)")
print(f"Accuracy: {np.mean(cv_results_2['test_accuracy']):.2%}")
print(f"Precision: {np.mean(cv_results_2['test_precision']):.2%}")
print(f"Recall: {np.mean(cv_results_2['test_recall']):.2%}")
print(f"F1 Score: {np.mean(cv_results_2['test_f1']):.2%}")

print("\nCross-Validation Results (3-Fold)")
print(f"Accuracy: {np.mean(cv_results_3['test_accuracy']):.2%}")
print(f"Precision: {np.mean(cv_results_3['test_precision']):.2%}")
print(f"Recall: {np.mean(cv_results_3['test_recall']):.2%}")
print(f"F1 Score: {np.mean(cv_results_3['test_f1']):.2%}")

print("\nCombined metric**")
print(f"Accuracy: {accuracy:.2%}")
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print(f"F1 Score: {f1:.2%}")

with open("svm_model.pkl", "wb") as model_file:
    pickle.dump(svm_pipeline, model_file)