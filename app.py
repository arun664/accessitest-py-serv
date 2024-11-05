from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from sentence_transformers import SentenceTransformer, util
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight Sentence-BERT model

# Load WCAG guidelines data at startup
with open('data/wcag.json', 'r') as f:
    wcag_data = json.load(f)

# Extract guideline texts for embedding
guideline_texts = []
for principle in wcag_data.get("principles", []):
    for guideline in principle.get("guidelines", []):
        title = guideline.get("title")
        if title:
            guideline_texts.append(title)

# Encode guideline texts
guideline_embeddings = model.encode(guideline_texts, convert_to_tensor=True)

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
    # Proceed with your evaluation logic...

    # Get issues from Axe-Core and Pa11y
    axe_issues = data.get('axe-core-issues', [])
    pa11y_issues = data.get('pa11y-issues', [])

    results = []

    # Function to evaluate issues
    def evaluate_issues(issues, source):
        for issue in issues:
            description = issue.get('description') or issue.get('help') or issue.get('message')
            if description:
                # Encode issue description
                issue_embedding = model.encode(description, convert_to_tensor=True)

                # Calculate cosine similarity
                similarities = util.cos_sim(issue_embedding, guideline_embeddings)
                most_similar_idx = similarities.argmax().item()
                similarity_score = similarities[0][most_similar_idx].item()

                # Determine if it's a true positive or false positive
                is_true_positive = similarity_score > 0.7  # Set a threshold for similarity

                results.append({
                    "source": source,
                    "issue": description,
                    "most_similar_guideline": guideline_texts[most_similar_idx],
                    "similarity_score": similarity_score,
                    "status": "True Positive" if is_true_positive else "False Positive"
                })

    # Evaluate Axe-Core issues
    evaluate_issues(axe_issues, source='Axe-Core')

    # Evaluate Pa11y issues
    evaluate_issues(pa11y_issues, source='Pa11y')

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
