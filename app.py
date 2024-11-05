from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from transformers import pipeline
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the zero-shot classification model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Load WCAG guidelines data at startup
with open('data/wcag.json', 'r') as f:
    wcag_data = json.load(f)

# Extract guideline texts for use as labels in classification
guideline_texts = []
for principle in wcag_data.get("principles", []):
    for guideline in principle.get("guidelines", []):
        title = guideline.get("title")
        if title:
            guideline_texts.append(title)

@app.route('/')
def index():
    return "Welcome to the Accessibility Evaluation API"

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Respond with "No Content" status

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    print('Received data:', data)  # Log the received data
    
    axe_issues = data.get('axe-core-issues', [])
    pa11y_issues = data.get('pa11y-issues', [])

    results = []

    # Function to evaluate issues using zero-shot classification
    def evaluate_issues(issues, source):
        for issue in issues:
            description = issue.get('description') or issue.get('help') or issue.get('message')
            if description:
                print(f"Evaluating {source} issue: {description}")

                # Define candidate labels for zero-shot classification
                candidate_labels = ["True Positive", "False Positive"]

                # Run zero-shot classification
                result = classifier(description, candidate_labels=candidate_labels)
                
                # Determine the classification result
                classification = result['labels'][0]  # First label is the most probable
                confidence = result['scores'][0]       # Confidence score of the classification

                # Find the most similar WCAG guideline
                guideline_result = classifier(description, candidate_labels=guideline_texts)
                most_similar_guideline = guideline_result['labels'][0]
                guideline_confidence = guideline_result['scores'][0]

                # Append the result
                results.append({
                    "source": source,
                    "issue": description,
                    "most_similar_guideline": most_similar_guideline,
                    "guideline_confidence": guideline_confidence,
                    "classification": classification,
                    "classification_confidence": confidence
                })

                # Log classification result for debugging
                print(f"Classification: {classification} (Confidence: {confidence})")
                print(f"Most Similar Guideline: {most_similar_guideline} (Confidence: {guideline_confidence})")
            else:
                print(f"Skipped {source} issue with missing description: {issue}")

    # Evaluate Axe-Core issues
    evaluate_issues(axe_issues, source='Axe-Core')

    # Evaluate Pa11y issues
    evaluate_issues(pa11y_issues, source='Pa11y')

    print("Evaluation Results:", results)  # Log full results for debugging

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
