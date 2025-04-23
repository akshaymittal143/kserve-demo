import joblib
import json
import numpy as np
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Load the model
model_path = os.environ.get('MODEL_PATH', '/app/model.joblib')
model = joblib.load(model_path)

@app.route('/v1/models/sentiment-classifier', methods=['GET'])
def health():
    return jsonify({"status": "ready"})

@app.route('/v1/models/sentiment-classifier:predict', methods=['POST'])
def predict():
    data = request.json
    
    # Extract instances from the request
    instances = data.get('instances', [])
    texts = [instance.get('text', '') for instance in instances]
    
    # Make predictions
    predictions = model.predict(texts)
    probabilities = model.predict_proba(texts)
    
    # Format the response
    results = []
    for i, pred in enumerate(predictions):
        results.append({
            'prediction': int(pred),
            'confidence': float(probabilities[i][pred])
        })
    
    return jsonify({"predictions": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)