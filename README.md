# Heart Disease Prediction Web Application

This web application predicts whether a patient has heart disease based on clinical parameters.

## Setup Instructions

1. Make sure you have Python installed on your system
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Jupyter notebook to train the model and generate the pickle file:
   ```
   jupyter notebook Heart_Disease_prediction.ipynb
   ```
   - Execute all cells
   - This will create `heart_disease_model.pkl` in your directory

4. Start the web application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Using the Application

1. Enter the patient's ID (for identification purposes only)
2. Fill in all the required health parameters
3. Click "Predict" to see the results

## Parameters Explanation

- **Age**: Age in years
- **Sex**: Gender (1 = male, 0 = female)
- **Chest Pain Type**: Type of chest pain (0-3)
- **Resting Blood Pressure**: Blood pressure in mm Hg
- **Cholesterol**: Serum cholesterol in mg/dl
- **Fasting Blood Sugar**: Whether fasting blood sugar > 120 mg/dl (1 = true, 0 = false)
- **Resting ECG Results**: Results of electrocardiogram at rest
- **Maximum Heart Rate**: Maximum heart rate achieved
- **Exercise Induced Angina**: Whether exercise induced angina (1 = yes, 0 = no)
- **ST Depression**: ST depression induced by exercise relative to rest
- **Slope of ST**: Slope of the peak exercise ST segment
- **Number of Major Vessels**: Number of major vessels (0-3) colored by fluoroscopy
