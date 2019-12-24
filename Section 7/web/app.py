from flask import Flask, jsonify, request
from flask_restful import Api, Resource
# from pymongo import MongoClient
# import bcrypt
import requests
import subprocess
import json

app = Flask(__name__)
api = Api(app)

# client = MongoClient("mongodb//db:27017")
# db = client.ImageRecognition
# users = db["Users"]

# def userExists(username):
#     if users.find({"Username": username}).count() == 0:
#         return False
#     else:
#         return True

# def verifyPassword(username, password):
#     if not userExists(username):
#         return False

#     hashed_password = users.find({
#         "Username": username
#     })[0]["Password"]

#     if bcrypt.hashpw(password.encode('utf8'), hashed_password) == hashed_password:
#         return True
#     else: 
#         return False

def generateReturnDictionary(status, message):
    return_json = {
        "Status Code": status, 
        "Message": message
    }
    return return_json

# def verifyCredentials(username, password):
#     if not userExists(username):
#         return generateReturnDictionary(401, "Invalid Username"), True

#     correct_password = verifyPassword(username, password)
#     if not correct_password:
#         return generateReturnDictionary(401, "Invalid Password"), True

#     return None, False

# class Register(Resource):
#     def post(self):
#         postedData = request.get_json()
#         username = postedData["username"]
#         password = postedData["password"]

#         if userExists(username):
#             return_json = {
#                 "Status Code": 400, 
#                 "Message": "User already exists"
#             }
#             return jsonify(return_json)

#         hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

#         users.insert({
#             "Username": username, 
#             "Password": hashed_password, 
#             "Tokens": 4
#         })

#         return_json = {
#             "Status Code": 200, 
#             "Message": "Registered successfully"
#         }
#         return jsonify(return_json)

class Classify(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["useranme"]
        password = postedData["password"]
        url = postedData["url"]

        # return_json, error = verifyCredentials(username, password)
        # if error:
        #     return jsonify(return_json)

        # tokens = users.find({
        #     "Username": username
        # })[0]["Tokens"]

        # if tokens <= 0:
        #     return jsonify( generateReturnDictionary(403, "Forbidden -- Not Enough Tokens"))

        r = requests.get(url)
        return_json = {}

        with open("temp.jpg", "wb") as f:
            f.write(r.content)
            proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg')
            proc.communicate()[0]
            proc.wait()
            with open("text.txt") as g:
                return_json = json.load(g)
        
        # users.update_one({
        #     "Username": username
        #     }, {
        #         "$set": {
        #             "Tokens": tokens - 1
        #             }
        #     })

        return return_json

# class Refill(Resource):
#     def post(self):
#         postedData = request.get_json()
#         username = postedData["username"]
#         password = postedData["admin_pw"]
#         amount = postedData["amount"]

#         if not userExists(username):
#             return jsonify( generateReturnDictionary(404, "User not found"))

#         if not password == "abc123":
#             return jsonify( generateReturnDictionary(401, "Invalid admin password"))

#         users.update_one({
#             "Username": username
#         }, {
#             "$set": {
#                 "Tokens": amount
#             }
#         })

#         return jsonify( generateReturnDictionary(200, "Refilled successfully") )

# api.add_resource(Register, "/register")
api.add_resource(Classify, "/classify")
# api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(host = "0.0.0.0")