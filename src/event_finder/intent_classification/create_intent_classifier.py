import json
import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.utils import compute_class_weight
from event_finder.utils.path import path_relative_to_root


data = []
file_path = path_relative_to_root("data/intent_data/sentences_with_labelled_intent.txt")
with open(file_path, 'r') as file:
    for line in file:
        data.append(json.loads(line))


df = pd.DataFrame(data)

X = df['sentence']
y = df['label']

enconding_model = SentenceTransformer('all-MiniLM-L6-v2')

X_encoded = enconding_model.encode(X.tolist())


X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42, stratify=y
)

classes = np.array([0,1])
class_weights = compute_class_weight('balanced', classes= classes, y=y_train)
class_weight_dict = {0: class_weights[0], 1: class_weights[1]}

clf = RandomForestClassifier(class_weight=class_weight_dict, random_state=42)
clf.fit(X_train, y_train)

model_file_path = path_relative_to_root("src/event_finder/intent_classification/models/random_forest_model.joblib")
joblib.dump(clf, model_file_path)

# Evaluate the model
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
