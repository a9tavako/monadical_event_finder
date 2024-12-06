import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils.class_weight import compute_class_weight
import json
import matplotlib.pyplot as plt
import numpy as np
from joblib import dump
from sentence_transformers import SentenceTransformer

  
data = []
file_path = "/Users/namra/Documents/monadical_project/ml_meeting_finder/data/intent_data/labelled_schedule_intent_sentences.txt"
with open(file_path, 'r') as file:
    for line in file:
        data.append(json.loads(line))

# Convert to a Pandas DataFrame
df = pd.DataFrame(data)

# Extract sentences and labels
X = df['sentence']
y = df['label']

enconding_model = SentenceTransformer('all-MiniLM-L6-v2')

X_encoded = enconding_model.encode(X.tolist())


# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42, stratify=y
)

# Compute class weights
classes = np.array([0,1])
class_weights = compute_class_weight('balanced', classes= classes, y=y_train)
class_weight_dict = {0: class_weights[0], 1: class_weights[1]}

# Train a Random Forest Classifier with class weights
clf = RandomForestClassifier(class_weight=class_weight_dict, random_state=42)
clf.fit(X_train, y_train)
model_file_path = "/Users/namra/Documents/monadical_project/ml_meeting_finder/source_code/models/random_forest_model.joblib"
dump(clf, model_file_path)

# Evaluate the model
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
