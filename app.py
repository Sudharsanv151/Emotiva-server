from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt
from transformers import pipeline

load_dotenv()  

app = Flask(__name__)
CORS(app)  
client = MongoClient(os.getenv("MONGO_URI"))
db = client["Emotiva"]
users_collection = db["users"]

sentiment_pipeline = pipeline("text-classification", model="michellejieli/emotion_text_classifier")

@app.route('/user/register', methods=['POST'])
def register():
    data = request.get_json()
    name, email, password = data["name"], data["email"], data["password"]
 
    if users_collection.find_one({"email": email}):
        return jsonify({"message": "User already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password
    })
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/user/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email, password = data["email"], data["password"]

    user = users_collection.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful", "user": user["name"]}), 200

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    patterns = data.get('patterns', '')

    try:
        result = sentiment_pipeline(patterns)
        sentiment = result[0]['label']  
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    recommendations = [
        {'type': 'meme', 'content': 'https://example.com/funny-meme.jpg'} if sentiment == 'POSITIVE' 
        else {'type': 'practice', 'content': 'Relaxation Exercise'}
    ]
    
    return jsonify({'sentiment': sentiment, 'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True)
