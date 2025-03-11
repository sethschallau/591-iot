# train_classifier.py
# need to collect real IMU data from your actual sensor while opening and closing the door.
# Save that data and replace this synthetic data generation with real data

import json
import random
import pickle
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

x = []
y = []

for _ in range(100):
  # Door open sample:
  x.append([random.uniform(1.5, 3.0), random.uniform(-1.0, 1.0), random.uniform(-0.5, 0.5), random.uniform(30, 60), random.uniform(0, 10), random.uniform(0, 10)])    # approximation of how a door might move
  y.append(1)  # 1 = open

  # Door close sample
  x.append([random.uniform(-3.0, -1.5), random.uniform(-1.0, 1.0), random.uniform(-0.5, 0.5), random.uniform(-60, -30), random.uniform(0, 10), random.uniform(0, 10)])   # approximation of how a door might move
  y.append(0)  # 0 = close

# Train-test split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)

# Train SVM classifier
clf = svm.SVC(kernel='linear')
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save model
with open("classifier.pkl", "wb") as f:
    pickle.dump(clf, f)
