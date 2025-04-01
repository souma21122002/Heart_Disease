from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()
# Add email functionality
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import logging
from email.mime.base import MIMEBase
from email import encoders
import base64
import re

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Email configuration
EMAIL_SENDER = os.getenv("EMAIL")
# This should be an app password, not your regular Gmail password
EMAIL_PASSWORD = os.getenv("PASSWORD")
DOCTOR_EMAIL = "s.f.meisser87@gmail.com"

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

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        # Get form data
        patient_id = request.form.get('patientid', 'Not provided')
        doctor_email = request.form.get('doctorEmail', DOCTOR_EMAIL)
        message = request.form.get('message', '')
        prediction_result = request.form.get('predictionResult', '')
        probability = request.form.get('probability', '')
        pdf_attachment = request.form.get('pdfAttachment', None)
        
        # Log the email request
        logger.info(f"Email request received for patient {patient_id} to {doctor_email}")
        
        # Create the email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Heart Health Assessment Results - Patient ID: {patient_id}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = doctor_email
        
        # Create HTML email content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .result {{ font-weight: bold; font-size: 18px; color: {'#d9534f' if 'High risk' in prediction_result else '#5cb85c'}; }}
                .footer {{ font-size: 12px; color: #777; border-top: 1px solid #eee; padding-top: 10px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Heart Health Assessment Results</h2>
                </div>
                <div class="content">
                    <p>Dear Doctor,</p>
                    <p>Please find the heart health assessment results for your patient (ID: {patient_id}):</p>
                    
                    <p class="result">{prediction_result}</p>
                    <p>Probability: {probability}</p>
                    
                    <p>Patient's message:</p>
                    <p>{message if message else 'No additional message provided.'}</p>
                    
                    <p>For more detailed information, please see the attached PDF report.</p>
                    
                    <p>Please review these results and advise the patient on next steps.</p>
                    <p>Thank you,</p>
                    <p>Heart Health Assessment Tool</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>The information contained in this email is for the exclusive use of the intended recipient and may contain confidential information. If you are not the intended recipient, please notify the sender immediately and destroy all copies.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Attach PDF if available
        if pdf_attachment:
            try:
                # Check if there's actual data in the attachment
                if len(pdf_attachment) < 100:
                    logger.error(f"PDF attachment data too short: {pdf_attachment}")
                    raise ValueError("Invalid PDF data")
                
                logger.info(f"PDF attachment data received. Length: {len(pdf_attachment)}")
                
                # Extract the base64 data from the data URL
                if 'data:application/pdf;base64,' in pdf_attachment:
                    # Standard data URI format
                    pdf_data = re.sub('^data:application/pdf;base64,', '', pdf_attachment)
                else:
                    # Try alternate format that might be used
                    pdf_data = re.sub('^data:base64,', '', pdf_attachment)
                    if pdf_data == pdf_attachment:  # If no substitution was made
                        # Just take everything after the comma if present
                        if ',' in pdf_attachment:
                            pdf_data = pdf_attachment.split(',', 1)[1]
                        else:
                            # Use as is, assuming it's already base64
                            pdf_data = pdf_attachment
                
                logger.info(f"PDF base64 data extracted. Length: {len(pdf_data)}")
                
                try:
                    # Try to decode the base64 data
                    pdf_bytes = base64.b64decode(pdf_data)
                    logger.info(f"PDF successfully decoded. Size: {len(pdf_bytes)} bytes")
                    
                    # Verify we have a valid PDF (check for PDF signature)
                    if not pdf_bytes.startswith(b'%PDF-'):
                        logger.warning("PDF does not start with %PDF- signature")
                        # Sometimes the signature might be in a different encoding or have extra bytes
                        # Try to find the PDF signature anywhere in the first 1024 bytes
                        if b'%PDF-' not in pdf_bytes[:1024]:
                            logger.error("Invalid PDF format - cannot find %PDF- signature")
                            # We'll still try to attach it
                
                    # Create the attachment
                    pdf_part = MIMEBase('application', 'pdf')
                    pdf_part.set_payload(pdf_bytes)
                    
                    # Encode and add headers
                    encoders.encode_base64(pdf_part)
                    pdf_part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="Heart_Assessment_Report_{patient_id}.pdf"'
                    )
                    
                    # Add the attachment to the message
                    msg.attach(pdf_part)
                    
                    logger.info("PDF attachment successfully added to email")
                except Exception as decode_error:
                    logger.error(f"Error decoding PDF base64 data: {str(decode_error)}")
                    logger.error(f"First 100 chars of PDF data: {pdf_data[:100]}")
                    raise
                
            except Exception as pdf_error:
                logger.error(f"Error attaching PDF: {str(pdf_error)}")
                # Continue with the email even if PDF attachment fails
                
        # Connect to Gmail SMTP server and send the email
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                # Login to sender email
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                
                # Send email
                server.sendmail(EMAIL_SENDER, doctor_email, msg.as_string())
                
                logger.info(f"Email sent successfully to {doctor_email}")
            
            # Create success response
            response = {
                'success': True,
                'message': f'Results sent to {doctor_email} with PDF attachment',
            }
            
            return jsonify(response)
            
        except Exception as smtp_error:
            logger.error(f"SMTP error: {str(smtp_error)}")
            return jsonify({
                'success': False, 
                'error': f"Email sending failed: {str(smtp_error)}"
            }), 500
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    app.run(debug=True)
