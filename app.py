from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable CORS for local testing
from transformers import pipeline

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for React frontend

# Load the Hugging Face sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    patterns = data.get('patterns', '')

    # NLP sentiment analysis
    try:
        result = sentiment_pipeline(patterns)
        sentiment = result[0]['label']  # 'POSITIVE' or 'NEGATIVE'
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Mock recommendations based on sentiment
    recommendations = [
        {'type': 'meme', 'content': 'https://example.com/funny-meme.jpg'} if sentiment == 'POSITIVE' 
        else {'type': 'practice', 'content': 'Relaxation Exercise'}
    ]
    return jsonify({'sentiment': sentiment, 'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True)
