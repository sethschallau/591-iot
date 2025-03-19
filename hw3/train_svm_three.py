import pandas as pd
import numpy as np
import pickle
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

df = pd.read_csv("raw_data/openingclosing.csv")
df["state"] = df["state"].map({"stable": 0, "opening": 1, "closing": 2})

def create_chunks(df, chunk_size=12):
    X, y = [], []
    i = 0
    while i <= len(df) - chunk_size:
        chunk = df.iloc[i:i + chunk_size]
        states = chunk["state"].unique()
        if len(states) == 1:
            features = chunk[["ax", "az", "gx", "gz"]].values.flatten()
            X.append(features)
            y.append(states[0])
            i += chunk_size
        else:
            i += 1
    return np.array(X), np.array(y)

X, y = create_chunks(df, chunk_size=12)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

svm_pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(kernel="rbf", C=1.0, gamma="scale"))
])

scoring = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
cv_results_2 = cross_validate(svm_pipeline, X_train, y_train, cv=2, scoring=scoring)
cv_results_3 = cross_validate(svm_pipeline, X_train, y_train, cv=3, scoring=scoring)

svm_pipeline.fit(X_train, y_train)
y_pred = svm_pipeline.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average="macro")
recall = recall_score(y_test, y_pred, average="macro")
f1 = f1_score(y_test, y_pred, average="macro")

print("\nCross-Validation Results (2-Fold)")
print(f"Accuracy: {np.mean(cv_results_2['test_accuracy']):.2%}")
print(f"Precision: {np.mean(cv_results_2['test_precision_macro']):.2%}")
print(f"Recall: {np.mean(cv_results_2['test_recall_macro']):.2%}")
print(f"F1 Score: {np.mean(cv_results_2['test_f1_macro']):.2%}")

print("\nCross-Validation Results (3-Fold)")
print(f"Accuracy: {np.mean(cv_results_3['test_accuracy']):.2%}")
print(f"Precision: {np.mean(cv_results_3['test_precision_macro']):.2%}")
print(f"Recall: {np.mean(cv_results_3['test_recall_macro']):.2%}")
print(f"F1 Score: {np.mean(cv_results_3['test_f1_macro']):.2%}")

print("\nTest Results")
print(f"Accuracy: {accuracy:.2%}")
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print(f"F1 Score: {f1:.2%}")

with open("svm_model.pkl", "wb") as model_file:
    pickle.dump(svm_pipeline, model_file)
