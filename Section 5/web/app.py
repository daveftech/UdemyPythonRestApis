"""
Regisration of a user 0 tokens
Each user gets 10 tokens
Store a sentence on our database for 1 token
Retrieve a user's stored sentence for 1 token
"""
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]

class Register(Resource):
    def post(self):
        # Unmarshal the data
        postData = request.get_json()

        # Get the data
        username = postData["username"]
        password = postData["password"]

        # Hash password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # Store the Username and Password
        users.insert({
            "Username" : username, 
            "Password" : hashed_pw, 
            "Sentence" : "", 
            "Tokens" : 6
        })

        # Return
        retJson = {
            "status" : 200, 
            "message" : "You successfully signed up"
        }

        return jsonify(retJson)

class Sentence(Resource):
    def post(self):
        # Unmarshal the data
        postData = request.get_json()

        # Get the data
        username = postData["username"]
        password = postData["password"]
        sentence = postData["sentence"]

        # Verify the username and password
        authenticated = authenticate(username, password)
        
        if not authenticated:
            retJson = {
                "status" : 409, 
                "message" : "Invalid password"
            }

            return jsonify(retJson)

        # Verify user token count
        num_tokens = count_tokens(username)
        
        if num_tokens <= 0:
            retJson = {
                "status" : 409, 
                "message" : "Not enough tokens"
            }

            return jsonify(retJson)


        # Store the sentence, decrement tokens and return
        users.update({
            "Username" : username
        }, {
            "$set" : {
                "Sentence" : sentence, 
                "Tokens" : num_tokens - 1
            }
        })

        retJson = {
            "status" : 200, 
            "message" : "Saved Successfully"
        }

        return jsonify(retJson)

class Get(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        authenticated = authenticate(username, password)

        if not authenticated:
            retJson = {
                "status" : 400, 
                "message" : "Invalid username or password"
            }

            return jsonify(retJson)

        num_tokens = count_tokens(username)

        if num_tokens <= 0:
            retJson = {
                "status" : 400, 
                "message" : "You have no tokens left"
            }

            return jsonify(retJson)

        sentence = users.find({
            "Username" : username
        })[0]["Sentence"]

        users.update({
            "Username" : username
        }, {
            "$set" : {
                "Tokens" : num_tokens - 1
            }
        })

        retJson = {
            "status" : 200, 
            "sentence" : sentence
        }

        return jsonify(retJson)

def authenticate(username, password):
    hashed_pw = users.find({
        "Username" : username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else: 
        return False

def count_tokens(username):
    tokens = users.find({
        "Username" : username
    })[0]["Tokens"]

    return tokens

api.add_resource(Register, "/register")
api.add_resource(Sentence, "/sentence")
api.add_resource(Get, "/get")

if __name__ == "__main__":
    app.run(host= '0.0.0.0')

"""
Previous application
"""
# from flask import Flask, jsonify, request
# from flask_restful import Resource, Api
# from pymongo import MongoClient

# app = Flask(__name__)
# api = Api(app)

# client = MongoClient("mongodb://db:27017")
# db = client.aNewDB
# UserNum = db["UserNum"]

# UserNum.insert({
#     'num_of_users': 0
# })

# class Visit(Resource): 
#     def get(self):
#         prev_num = UserNum.find({})[0]['num_of_users']
#         new_num = prev_num + 1
#         UserNum.update({}, {'$set':{"num_of_users":new_num}})
#         return str(f"Hello user number: {new_num}")

# def checkPostedData(postedData, functionName):
#     if(functionName.lower() == "add" or functionName.lower() == "subtract" or functionName.lower() == "multiply"):
#         if "x" not in postedData or "y" not in postedData:
#             return 400
#         else:
#             return 200
#     elif(functionName.lower() == "divide"):
#         if "x" not in postedData or "y" not in postedData or postedData["y"] == 0:
#             return 400
#         else:
#             return 200

#     return 400

# class Add(Resource):
#     def post(self):
#         # Get the posted data
#         postedData = request.get_json()

#         # Validate the posted data
#         status_code = checkPostedData(postedData, "add")

#         # Handle validation errors
#         if status_code != 200:
#             return_json = {
#                 "Message": "An error has occurred", 
#                 "Status Code": status_code
#             }

#             return jsonify(return_json)

#         # Process the data
#         x = postedData["x"]
#         y = postedData["y"]

#         x = int(x)
#         y = int(y)

#         result = x + y

#         # Prepare the response
#         return_map = {
#             'Message': result, 
#             'Status Code': 200
#         }
        
#         # Return the response
#         return jsonify(return_map)

#     def get(self):
#         return_map = {
#             'Message': 'This method can be used to add two integers together', 
#             'Status Code': 200
#         }

#         return jsonify(return_map)

# class Subtract(Resource):
#     def post(self):
#         # Get the posted data
#         postedData = request.get_json()

#         # Validate the posted data
#         status_code = checkPostedData(postedData, "subtract")

#         # Handle validation errors
#         if status_code != 200:
#             return_json = {
#                 "Message": "An error has occurred", 
#                 "Status Code": status_code
#             }

#             return jsonify(return_json)

#         # Process the data
#         x = postedData["x"]
#         y = postedData["y"]

#         x = int(x)
#         y = int(y)

#         result = x - y

#         # Prepare the response
#         return_map = {
#             'Message': result, 
#             'Status Code': 200
#         }
        
#         # Return the response
#         return jsonify(return_map)

# class Multiply(Resource):
#     def post(self):
#         # Get the posted data
#         postedData = request.get_json()

#         # Validate the posted data
#         status_code = checkPostedData(postedData, "multiply")

#         # Handle validation errors
#         if status_code != 200:
#             return_json = {
#                 "Message": "An error has occurred", 
#                 "Status Code": status_code
#             }

#             return jsonify(return_json)

#         # Process the data
#         x = postedData["x"]
#         y = postedData["y"]

#         x = int(x)
#         y = int(y)

#         result = x * y

#         # Prepare the response
#         return_map = {
#             'Message': result, 
#             'Status Code': 200
#         }
        
#         # Return the response
#         return jsonify(return_map)

# class Divide(Resource):
#     def post(self):
#         # Get the posted data
#         postedData = request.get_json()

#         # Validate the posted data
#         status_code = checkPostedData(postedData, "divide")

#         # Handle validation errors
#         if status_code != 200:
#             return_json = {
#                 "Message": "An error has occurred", 
#                 "Status Code": status_code
#             }

#             return jsonify(return_json)

#         # Process the data
#         x = postedData["x"]
#         y = postedData["y"]

#         x = int(x)
#         y = int(y)

#         result = x / y

#         # Prepare the response
#         return_map = {
#             'Message': result, 
#             'Status Code': 200
#         }
        
#         # Return the response
#         return jsonify(return_map)

# api.add_resource(Add, "/add")
# api.add_resource(Subtract, "/subtract")
# api.add_resource(Multiply, "/multiply")
# api.add_resource(Divide, "/divide")
# api.add_resource(Visit, "/hello")

# @app.route('/')
# def hello_world():
#     return "Hello world!"


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)