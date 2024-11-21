from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt
from bson import ObjectId

load_dotenv()

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["Emotiva"]
users_collection = db["users"]
journals_collection = db["journals"]

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

    return jsonify({
        "message": "Login successful", 
        "user": user["name"], 
        "email": email
    }), 200

@app.route('/journals/add', methods=['POST'])
def add_journal():
    data = request.get_json()

    if 'email' not in data:
        return jsonify({"message": "Email is required"}), 400

    email = data["email"]
    journal = {
        "email": email,
        "title": data["title"],
        "content": data["content"],
        "timestamp": data["timestamp"]
    }

    try:
        journals_collection.insert_one(journal)
        return jsonify({"message": "Journal added successfully"}), 201
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/journals/get', methods=['POST'])
def get_journals():
    data = request.get_json()
    email = data["email"]

    user_journals = list(journals_collection.find(
        {"email": email}, 
        {"_id": 1, "title": 1, "content": 1, "timestamp": 1}
    ))

    for journal in user_journals:
        journal['_id'] = str(journal['_id'])

    return jsonify({"journals": user_journals}), 200

@app.route('/journals/delete/<journal_id>', methods=['DELETE'])
def delete_journal(journal_id):
    try:
        result = journals_collection.delete_one({"_id": ObjectId(journal_id)})
        if result.deleted_count == 1:
            return jsonify({"message": "Journal deleted successfully"}), 200
        else:
            return jsonify({"message": "Journal not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/journals/update/<journal_id>', methods=['PUT'])
def update_journal(journal_id):
    try:
        data = request.get_json()
        result = journals_collection.update_one(
            {"_id": ObjectId(journal_id)},
            {"$set": {"title": data["title"], "content": data["content"]}}
        )
        if result.matched_count:
            return jsonify({"message": "Journal updated successfully"}), 200
        else:
            return jsonify({"message": "Journal not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error updating journal: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)