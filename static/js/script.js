document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    const resultDiv = document.getElementById('result');
    const resultMessage = document.getElementById('result-message');
    const resultProbability = document.getElementById('result-probability');
    const patientInfo = document.getElementById('patient-info');
    
    // Define mappings for all dropdowns with exact input values
    const dropdownMappings = {
        'cp': {  // Chest pain type
            'Typical Angina': 'Typical Angina (1)', // Adding typical angina if it exists
            'Atypical Angina': 'Atypical Angina (2)',
            'Non-anginal Pain': 'Non-anginal Pain (1)',
            'Asymptomatic': 'Asymptomatic (0)'
        },
        'restecg': {  // Resting ECG results
            'Normal': 'Normal (0)',
            'ST-T Wave Abnormality': 'ST-T Wave Abnormality (1)',
            'Left Ventricular Hypertrophy': 'Left Ventricular Hypertrophy (2)'
        },
        'slope': {  // Slope of peak exercise ST segment
            'Upsloping': 'Upsloping (1)',
            'Flat': 'Flat (2)',
            'Downsloping': 'Downsloping (3)'
        },
        'thal': {  // Thalassemia
            'Normal': 'Normal (3)',
            'Fixed Defect': 'Fixed Defect (6)',
            'Reversible Defect': 'Reversible Defect (7)'
        },
        'exang': {  // Exercise induced angina
            'Yes': 'Yes (1)',
            'No': 'No (0)'
        },
        'fbs': {  // Fasting blood sugar
            'Yes': 'Yes (1)',
            'No': 'No (0)'
        },
        'sex': {  // Sex
            'Male': 'Male (1)',
            'Female': 'Female (0)'
        }
    };
    
    // Update all dropdowns with appropriate input values
    const dropdowns = form.querySelectorAll('select');
    dropdowns.forEach(dropdown => {
        // For any dropdown that doesn't have explicit mappings, add default numbered options
        if (!dropdownMappings[dropdown.id]) {
            // Create a mapping for this dropdown by numbering the options
            const autoMapping = {};
            Array.from(dropdown.options).forEach((option, index) => {
                autoMapping[option.text] = `${option.text} (${option.value || index})`;
            });
            dropdownMappings[dropdown.id] = autoMapping;
        }
        
        // Apply the mappings
        const mappings = dropdownMappings[dropdown.id];
        Array.from(dropdown.options).forEach(option => {
            if (mappings[option.text]) {
                option.text = mappings[option.text];
            }
        });
    });
    
    // Add healthcare UI improvements
    enhanceHealthcareUI();
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get patient ID for display purposes
        const patientId = document.getElementById('patientid').value;
        
        // Collect all form data
        const formData = new FormData(form);
        
        // Convert formData to an object for later use in visualizations
        const formDataObj = {};
        for (const [key, value] of formData.entries()) {
            formDataObj[key] = value;
        }
        
        // Send data to server
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Display result
            resultMessage.textContent = data.message;
            resultMessage.className = data.prediction === 1 ? 'high-risk' : 'low-risk';
            resultProbability.textContent = `Probability: ${(data.probability * 100).toFixed(2)}%`;
            
            // Display patient ID if provided
            if (patientId) {
                patientInfo.innerHTML = `<p>Patient ID: ${patientId}</p>`;
            } else {
                patientInfo.innerHTML = '';
            }
            
            // Add personalized health suggestions based on risk level
            addHealthSuggestions(data.prediction, data.probability, formDataObj);
            
            // Add visualization elements
            createVisualization(formDataObj, data.probability);
            
            resultDiv.classList.remove('hidden');
            
            // Scroll to result
            resultDiv.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during prediction. Please try again.');
        });
    });
    
    // Function to enhance the UI with healthcare styling
    function enhanceHealthcareUI() {
        // Add a friendly healthcare header
        const headerDiv = document.createElement('div');
        headerDiv.className = 'healthcare-header';
        headerDiv.innerHTML = `
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #0066cc; margin-bottom: 10px;">Heart Health Assessment</h2>
                <p style="color: #555; max-width: 800px; margin: 0 auto;">
                    This tool helps you understand your heart health risks. 
                    Enter your information below for a personalized assessment.
                </p>
            </div>
        `;
        
        // Insert the header before the form
        form.parentNode.insertBefore(headerDiv, form);
        
        // Add a container for health suggestions
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.id = 'health-suggestions';
        suggestionsDiv.className = 'hidden';
        suggestionsDiv.style.margin = '25px 0';
        suggestionsDiv.style.padding = '20px';
        suggestionsDiv.style.borderRadius = '8px';
        suggestionsDiv.style.backgroundColor = '#f9f9f9';
        
        // Add a container for visualizations
        const visualizationDiv = document.createElement('div');
        visualizationDiv.id = 'visualization-container';
        visualizationDiv.className = 'hidden';
        visualizationDiv.style.margin = '25px 0';
        
        // Insert these elements after the result div
        resultDiv.parentNode.insertBefore(suggestionsDiv, resultDiv.nextSibling);
        resultDiv.parentNode.insertBefore(visualizationDiv, suggestionsDiv.nextSibling);
        
        // Add a disclaimer at the bottom
        const disclaimerDiv = document.createElement('div');
        disclaimerDiv.style.fontSize = '12px';
        disclaimerDiv.style.color = '#777';
        disclaimerDiv.style.textAlign = 'center';
        disclaimerDiv.style.margin = '30px 0 20px';
        disclaimerDiv.innerHTML = `
            <p>
                <strong>Disclaimer:</strong> This tool provides an estimate only and does not replace 
                professional medical advice. Always consult with your healthcare provider.
            </p>
        `;
        
        document.querySelector('body').appendChild(disclaimerDiv);
        
        // Load Chart.js for visualizations
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        document.head.appendChild(script);
    }
    
    // Function to add personalized health suggestions
    function addHealthSuggestions(prediction, probability, formData) {
        const suggestionsDiv = document.getElementById('health-suggestions');
        const riskLevel = prediction === 1 ? 'high' : 'low';
        const riskPercentage = (probability * 100).toFixed(1);
        
        let suggestionsHTML = `
            <h3 style="color: #0066cc; margin-bottom: 15px;">Personalized Health Recommendations</h3>
        `;
        
        // General recommendations for all risk levels
        const generalSuggestions = [
            "Maintain a heart-healthy diet rich in fruits, vegetables, whole grains, and lean proteins.",
            "Aim for at least 150 minutes of moderate exercise per week.",
            "Monitor and manage your blood pressure and cholesterol levels.",
            "Avoid smoking and limit alcohol consumption.",
            "Manage stress through relaxation techniques, adequate sleep, and social connections."
        ];
        
        // Specific recommendations based on risk factors in the form data
        const specificSuggestions = [];
        
        if (formData.age > 50) {
            specificSuggestions.push("Consider regular heart check-ups as age is a significant risk factor.");
        }
        
        if (formData.chol > 200) {
            specificSuggestions.push("Your cholesterol level is elevated. Consider dietary changes and consult your doctor about management options.");
        }
        
        if (formData.trestbps > 130) {
            specificSuggestions.push("Your blood pressure reading is above optimal levels. Regular monitoring and lifestyle modifications are recommended.");
        }
        
        if (formData.thalach < 150) {
            specificSuggestions.push("Your maximum heart rate during exercise is lower than average. Gradual, supervised exercise may help improve cardiac fitness.");
        }
        
        // Add risk-level specific content
        if (riskLevel === 'high') {
            suggestionsHTML += `
                <p style="color: #d9534f; font-weight: bold; margin-bottom: 15px;">
                    Your assessment indicates a higher risk (${riskPercentage}%) for heart disease. 
                    Please consult with a healthcare provider promptly.
                </p>
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #333; margin-bottom: 10px;">Priority Actions:</h4>
                    <ul style="padding-left: 20px; color: #555;">
                        <li>Schedule an appointment with a cardiologist for a comprehensive evaluation.</li>
                        <li>Discuss medication options with your healthcare provider if not already prescribed.</li>
                        <li>Consider cardiac rehabilitation programs if recommended by your doctor.</li>
                        <li>Make immediate lifestyle changes to reduce risk factors.</li>
                    </ul>
                </div>
            `;
        } else {
            suggestionsHTML += `
                <p style="color: #5cb85c; font-weight: bold; margin-bottom: 15px;">
                    Your assessment indicates a lower risk (${riskPercentage}%) for heart disease. 
                    Continue with preventive measures to maintain heart health.
                </p>
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #333; margin-bottom: 10px;">Preventive Actions:</h4>
                    <ul style="padding-left: 20px; color: #555;">
                        <li>Maintain your current heart-healthy practices.</li>
                        <li>Continue with regular health check-ups.</li>
                        <li>Stay physically active and maintain a healthy weight.</li>
                    </ul>
                </div>
            `;
        }
        
        // Add general recommendations
        suggestionsHTML += `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #333; margin-bottom: 10px;">General Heart Health Recommendations:</h4>
                <ul style="padding-left: 20px; color: #555;">
                    ${generalSuggestions.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
        `;
        
        // Add specific recommendations if any
        if (specificSuggestions.length > 0) {
            suggestionsHTML += `
                <div>
                    <h4 style="color: #333; margin-bottom: 10px;">Specific Recommendations Based on Your Profile:</h4>
                    <ul style="padding-left: 20px; color: #555;">
                        ${specificSuggestions.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        suggestionsDiv.innerHTML = suggestionsHTML;
        suggestionsDiv.classList.remove('hidden');
    }
    
    // Function to create visualizations
    function createVisualization(formData, probability) {
        const container = document.getElementById('visualization-container');
        container.innerHTML = `
            <h3 style="color: #0066cc; margin-bottom: 20px; text-align: center;">Your Health Metrics Visualization</h3>
            <div style="display: flex; flex-wrap: wrap; justify-content: space-around;">
                <div style="width: 45%; min-width: 300px; margin-bottom: 20px;">
                    <canvas id="riskChart" width="400" height="400"></canvas>
                </div>
                <div style="width: 45%; min-width: 300px; margin-bottom: 20px;">
                    <canvas id="factorsChart" width="400" height="400"></canvas>
                </div>
            </div>
        `;
        
        container.classList.remove('hidden');
        
        // Wait for Chart.js to load
        function waitForChart() {
            if (window.Chart) {
                createRiskChart(probability);
                createFactorsChart(formData);
            } else {
                setTimeout(waitForChart, 100);
            }
        }
        
        waitForChart();
    }
    
    // Risk probability gauge chart
    function createRiskChart(probability) {
        const ctx = document.getElementById('riskChart').getContext('2d');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Risk', 'Safe'],
                datasets: [{
                    data: [probability, 1 - probability],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(75, 192, 192, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                circumference: 180,
                rotation: -90,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Heart Disease Risk Probability',
                        font: { size: 16 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                return (value * 100).toFixed(1) + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Key health factors chart
    function createFactorsChart(formData) {
        const ctx = document.getElementById('factorsChart').getContext('2d');
        
        // Reference values for comparison (approximate healthy ranges)
        const references = {
            age: { min: 20, max: 80, optimal: 20, label: 'Age' },
            trestbps: { min: 90, max: 200, optimal: 120, label: 'Blood Pressure' },
            chol: { min: 100, max: 300, optimal: 180, label: 'Cholesterol' },
            thalach: { min: 80, max: 220, optimal: 170, label: 'Max Heart Rate' }
        };
        
        // Normalize values to percentage of reference range
        const normalizeValue = (value, factor) => {
            const ref = references[factor];
            // Invert values where lower is better (like cholesterol)
            if (factor === 'thalach') {
                return ((value - ref.min) / (ref.max - ref.min)) * 100;
            } else {
                // For values where higher is worse (age, BP, cholesterol)
                return ((value - ref.min) / (ref.max - ref.min)) * 100;
            }
        };
        
        // Get factors to display
        const factorsToDisplay = ['age', 'trestbps', 'chol', 'thalach'];
        const labels = factorsToDisplay.map(f => references[f].label);
        const userData = factorsToDisplay.map(f => normalizeValue(formData[f], f));
        const optimalData = factorsToDisplay.map(f => normalizeValue(references[f].optimal, f));
        
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Your Metrics',
                        data: userData,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                    },
                    {
                        label: 'Optimal Range',
                        data: optimalData,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(75, 192, 192, 1)'
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Key Health Metrics Comparison',
                        font: { size: 16 }
                    }
                }
            }
        });
    }
});
