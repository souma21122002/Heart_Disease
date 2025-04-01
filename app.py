from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load the model
model_path = os.path.join(os.path.dirname(__file__), 'heart_disease_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Get form data (excluding patient ID)
    features = []
    for feature in model.feature_names_in_:
        features.append(float(request.form.get(feature)))
    
    # Make prediction
    features_array = np.array([features])
    prediction = model.predict(features_array)[0]
    probability = model.predict_proba(features_array)[0][1]
    
    result = {
        'prediction': int(prediction),
        'probability': float(probability),
        'message': 'High risk of heart disease' if prediction == 1 else 'Low risk of heart disease'
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
