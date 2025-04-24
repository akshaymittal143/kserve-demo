"""
A sentiment analysis model training script that creates and saves a basic text classification pipeline.

This script creates a simple sentiment analysis model using scikit-learn's Pipeline, 
combining CountVectorizer for text feature extraction and MultinomialNB for classification.
The model is trained on a small sample dataset of product reviews and their corresponding
sentiment labels (positive/negative).

The trained model is saved to disk using joblib for later use in sentiment prediction tasks.

Dataset:
    texts: List of product review strings
    labels: Binary labels where 1 represents positive sentiment and 0 represents negative sentiment

Pipeline Components:
    - CountVectorizer: Converts text documents to a matrix of token counts
    - MultinomialNB: Naive Bayes classifier for discrete features

Outputs:
    - Saves the trained model pipeline to 'sentiment-model-v1/model.joblib'

Usage:
    Run this script directly to train and save the model:
    $ python train_model_v1.py

Requirements:
    - numpy
    - pandas
    - scikit-learn
    - joblib
"""

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