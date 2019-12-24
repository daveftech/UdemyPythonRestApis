from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

# Set up the API/Flask
app = Flask(__name__)
api = Api(app)

# Set up the database
client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db["Users"]

# Helper functions

# Check to see if the user exists in the DB
def userExists(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True

# Verify the password in the DB
def verifyPassword(username, password):
    if not userExists(username): 
        return False
    
    hashed_password = users.find({"Username": username})[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_password) == hashed_password:
        return True
    else:
        return False

# Get the token count from the DB
def countTokens(username):
    tokens = users.find({
        "Username": username
    })[0]["Tokens"]

    return tokens

# API Resources and Methods

class Register(Resource):
    def post(self):
        # Get the posted data
        postedData = request.get_json()
        username = postedData['username']
        password = postedData['password']

        # Check to see if the user exists
        if userExists(username):
            return_json = {
                "Status Code": 400, 
                "Message": "User already exists"
            }
            return jsonify(return_json)

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # Insert the user into the database
        users.insert({
            "Username": username, 
            "Password": hashed_password, 
            "Tokens": 6
        })

        # Return the result
        return_json = {
            "Status Code": 200, 
            "Message": "You have successfully registered."
        }
        return jsonify(return_json)

class Detect(Resource):
    def post(self):
        # Get the posted data
        postedData = request.get_json()
        print(postedData)
        username = postedData['username']
        password = postedData['password']
        text1 = postedData['text1']
        text2 = postedData['text2']

        print(f"Username: {username}, Password: {password}, Text 1: {text1}, Text 2: {text2}")

        # Validation
        if not userExists(username):
            return_json = {
                "Status Code": 400, 
                "Message": "Invalid username"
            }
            return jsonify(return_json)

        print("Validated")

        # Authentication
        if not verifyPassword(username, password): 
            return_json = {
                "Status Code": 400, 
                "Message": "Invalid password"
            }
            return jsonify(return_json)

        print("Authenticated")

        # Authorization
        if countTokens(username) <= 0:
            return_json = {
                "Status Code": 400, 
                "Message": "Out of tokens"
            }
            return jsonify(return_json)

        print("Authorized")

        # Setup and use our NLP model
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)

        ratio = text1.similarity(text2)

        print(f"Ratio calculated. Ratio: {ratio}")

        # Update the tokens
        current_tokens = countTokens(username)
        users.update_one({
            "Username": username
        }, {
            "$set": {
                "Tokens": current_tokens - 1
            }
        })

        print(f"Tokens updated.  Current tokens: {current_tokens - 1}")

        # Return the result
        return_json = {
            "Status Code": 200, 
            "Similarity": ratio, 
            "Message": "Similarity score calculated successfully"
        }

        return jsonify(return_json)

class Refill(Resource):
    def post(self):
        # Get the posted data
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["admin_pw"]
        refill_amount = postedData["refill"]

        # Validation
        if not userExists(username):
            return_json = {
                "Status Code": 400, 
                "Message": "Invalid username"
            }
            return jsonify(return_json)

        # Authentication
        # TODO Remove the hardcoded admin password
        correct_pw = "abc123"
        if not password == correct_pw:
            return_json = {
                "Status Code": 400, 
                "Message": "Invalid admin password"
            }
            return jsonify(return_json)

        # Update the tokens in the db
        current_tokens = countTokens(username)
        users.update({
            "Username": username
            }, {
                "$set": {
                    "Tokens": refill_amount + current_tokens
                }
            })

        # Return the result
        return_json = {
            "Status Code": 200, 
            "Message": "Refilled tokens successfully"
        }
        return jsonify(return_json)


# Setup and run the API
api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')

if __name__ == "__main__":
    app.run(host='0.0.0.0')