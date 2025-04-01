from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load the model
model_path = os.path.join(os.path.dirname(__file__), 'heart_disease_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# Define validation ranges based on the dataset
validation_ranges = {
    'age': (20, 80),
    'gender': (0, 1),
    'chestpain': (0, 3),
    'trestbps': (94, 200),
    'chol': (0, 602),
    'fbs': (0, 1),
    'restecg': (0, 2),
    'thalach': (71, 202),
    'exang': (0, 1),
    'oldpeak': (0, 6.2),
    'slope': (0, 3),
    'ca': (0, 3)
}

def get_recommendations(probability, prediction, features):
    """Generate personalized recommendations based on risk level and features"""
    risk_percentage = probability * 100
    age = features[0]
    gender = features[1]
    cholesterol = features[4]
    blood_sugar = features[5]
    
    lifestyle_recs = []
    monitoring_recs = []
    medical_recs = []
    
    # Age-specific recommendations
    if age > 60:
        lifestyle_recs.append("Consider low-impact exercises like swimming or walking")
        if risk_percentage > 50:
            monitoring_recs.append("More frequent check-ups recommended for seniors with elevated risk")
    else:
        lifestyle_recs.append("Regular moderate to vigorous exercise is recommended")
    
    # Cholesterol-specific recommendations
    if cholesterol > 200:
        lifestyle_recs.append("Focus on reducing saturated fat and increasing fiber in your diet")
        lifestyle_recs.append("Consider foods rich in omega-3 fatty acids")
        monitoring_recs.append("Regular cholesterol monitoring every 3-6 months")
        
    # Blood sugar-specific recommendations
    if blood_sugar == 1:
        lifestyle_recs.append("Monitor carbohydrate intake and follow a balanced diet")
        lifestyle_recs.append("Maintain regular meal times to help control blood sugar")
        monitoring_recs.append("Regular blood glucose testing as advised by your doctor")
    
    # General recommendations based on risk
    if risk_percentage < 30:
        medical_recs.append("Discuss these results at your next regular check-up")
        medical_recs.append("Continue preventive healthcare measures")
    elif risk_percentage < 70:
        medical_recs.append("Schedule an appointment with your doctor within the next month")
        medical_recs.append("Consider discussing preventive medications with your healthcare provider")
    else:
        medical_recs.append("Seek prompt medical attention to discuss these results")
        medical_recs.append("Consult with a cardiologist for specialized care")
        
    return {
        "lifestyle": lifestyle_recs,
        "monitoring": monitoring_recs,
        "medical": medical_recs
    }

def get_contributing_factors(features, prediction):
    """Identify key contributing factors for the prediction"""
    # Extract features for easier reference
    age, gender, chestpain, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca = features
    
    factors = []
    
    # Only include factors that significantly contribute to the prediction
    if age > 60:
        factors.append({
            "name": "Age",
            "value": f"{int(age)} years",
            "description": "Age is a significant risk factor for heart disease.",
            "impact": "high",
            "icon": "👴"
        })
    
    if chol > 240:
        factors.append({
            "name": "Cholesterol",
            "value": f"{int(chol)} mg/dl",
            "description": "Cholesterol is significantly above recommended levels.",
            "impact": "high",
            "icon": "🔴"
        })
    elif chol > 200:
        factors.append({
            "name": "Cholesterol",
            "value": f"{int(chol)} mg/dl",
            "description": "Cholesterol is above optimal levels.",
            "impact": "medium",
            "icon": "🟠"
        })
    
    if trestbps >= 140:
        factors.append({
            "name": "Blood Pressure",
            "value": f"{int(trestbps)} mm Hg",
            "description": "Blood pressure is in the hypertension range.",
            "impact": "high",
            "icon": "📈"
        })
    
    if exang == 1:
        factors.append({
            "name": "Exercise Angina",
            "value": "Present",
            "description": "Chest pain during exercise indicates restricted blood flow to the heart.",
            "impact": "high",
            "icon": "⚡"
        })
    
    if ca > 0:
        factors.append({
            "name": "Major Vessels",
            "value": f"{int(ca)}",
            "description": f"{int(ca)} major blood vessel(s) show significant blockage.",
            "impact": "high",
            "icon": "🚧"
        })
    
    if oldpeak > 2:
        factors.append({
            "name": "ST Depression",
            "value": f"{oldpeak:.1f}",
            "description": "Significant ST depression indicates abnormal heart activity during exercise.",
            "impact": "high", 
            "icon": "📉"
        })
    
    return factors

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Expected feature names (must match the model's training features)
        feature_names = ['age', 'gender', 'chestpain', 'trestbps', 'chol', 'fbs', 
                         'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca']
        
        # Get form data
        features = []
        for feature in feature_names:
            value = request.form.get(feature)
            # Check if value exists and is not empty
            if value is None or value == '':
                return jsonify({
                    'error': f"Missing required parameter: {feature}"
                }), 400
            
            # Convert value to float
            try:
                value = float(value)
            except ValueError:
                return jsonify({
                    'error': f"Invalid value for {feature}: {value}. Must be a number."
                }), 400
                
            # Validate the range
            min_val, max_val = validation_ranges.get(feature, (float('-inf'), float('inf')))
            if value < min_val or value > max_val:
                return jsonify({
                    'error': f"Value for {feature} must be between {min_val} and {max_val}."
                }), 400
                
            features.append(value)
        
        # Make prediction
        features_array = np.array([features])
        prediction = model.predict(features_array)[0]
        probability = model.predict_proba(features_array)[0][1]
        
        # Generate personalized recommendations and contributing factors
        recommendations = get_recommendations(probability, prediction, features)
        contributing_factors = get_contributing_factors(features, prediction)
        
        # Calculate model confidence (simplified for demonstration)
        confidence = 85 + (5 * abs(probability - 0.5) * 2)  # Higher confidence the further from 0.5
        
        result = {
            'prediction': int(prediction),
            'probability': float(probability),
            'message': 'High risk of heart disease' if prediction == 1 else 'Low risk of heart disease',
            'recommendations': recommendations,
            'contributing_factors': contributing_factors,
            'confidence': float(confidence)
        }
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error during prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
