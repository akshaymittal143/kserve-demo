import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os

# Enhanced dataset for text classification
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
    "Exceeded all my expectations",
    # Additional training data
    "The product quality is excellent",
    "Customer service was unhelpful",
    "Item arrived damaged and unusable",
    "Very satisfied with my purchase",
    "Easy to use and works perfectly"
]

labels = [1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1]  # 1: positive, 0: negative

# Create an improved pipeline with TF-IDF
improved_model = Pipeline([
    ('vectorizer', TfidfVectorizer(ngram_range=(1, 2))),  # Use bigrams
    ('classifier', MultinomialNB())
])

# Train the model
improved_model.fit(texts, labels)

# Create model directory
os.makedirs("sentiment-model-v2", exist_ok=True)

# Save the model
joblib.dump(improved_model, 'sentiment-model-v2/model.joblib')

print("Improved model saved to 'sentiment-model-v2/model.joblib'")