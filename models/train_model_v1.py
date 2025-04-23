import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os

# Sample dataset for text classification
texts = [
    "I love this product, it's amazing",
    "Great service and fast delivery",
    "This is terrible, doesn't work at all",
    "Awful experience, never buying again",
    "Fantastic customer support",
    "Disappointed with the quality",
    "Best purchase I've made this year",
    "Would recommend to everyone",
    "Complete waste of money",
    "Exceeded all my expectations"
]

labels = [1, 1, 0, 0, 1, 0, 1, 1, 0, 1]  # 1: positive, 0: negative

# Create a simple pipeline
model = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', MultinomialNB())
])

# Train the model
model.fit(texts, labels)

# Create model directory
os.makedirs("sentiment-model-v1", exist_ok=True)

# Save the model
joblib.dump(model, 'sentiment-model-v1/model.joblib')

print("Model saved to 'sentiment-model-v1/model.joblib'")