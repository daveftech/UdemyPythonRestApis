from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.aNewDB
UserNum = db["UserNum"]

UserNum.insert({
    'num_of_users': 0
})

class Visit(Resource): 
    def get(self):
        prev_num = UserNum.find({})[0]['num_of_users']
        new_num = prev_num + 1
        UserNum.update({}, {'$set':{"num_of_users":new_num}})
        return str(f"Hello user number: {new_num}")

def checkPostedData(postedData, functionName):
    if(functionName.lower() == "add" or functionName.lower() == "subtract" or functionName.lower() == "multiply"):
        if "x" not in postedData or "y" not in postedData:
            return 400
        else:
            return 200
    elif(functionName.lower() == "divide"):
        if "x" not in postedData or "y" not in postedData or postedData["y"] == 0:
            return 400
        else:
            return 200

    return 400

class Add(Resource):
    def post(self):
        # Get the posted data
        postedData = request.get_json()

        # Validate the posted data
        status_code = checkPostedData(postedData, "add")

        # Handle validation errors
        if status_code != 200:
            return_json = {
                "Message": "An error has occurred", 
                "Status Code": status_code
            }

            return jsonify(return_json)

        # Process the data
        x = postedData["x"]
        y = postedData["y"]

        x = int(x)
        y = int(y)

        result = x + y

        # Prepare the response
        return_map = {
            'Message': result, 
            'Status Code': 200
        }
        
        # Return the response
        return jsonify(return_map)

    def get(self):
        return_map = {
            'Message': 'This method can be used to add two integers together', 
            'Status Code': 200
        }

        return jsonify(return_map)

class Subtract(Resource):
    def post(self):
        # Get the posted data
        postedData = request.get_json()

        # Validate the posted data
        status_code = checkPostedData(postedData, "subtract")

        # Handle validation errors
        if status_code != 200:
            return_json = {
                "Message": "An error has occurred", 
                "Status Code": status_code
            }

            return jsonify(return_json)

        # Process the data
        x = postedData["x"]
        y = postedData["y"]

        x = int(x)
        y = int(y)

        result = x - y

        # Prepare the response
        return_map = {
            'Message': result, 
            'Status Code': 200
        }
        
        # Return the response
        return jsonify(return_map)

class Multiply(Resource):
    def post(self):
        # Get the posted data
        postedData = request.get_json()

        # Validate the posted data
        status_code = checkPostedData(postedData, "multiply")

        # Handle validation errors
        if status_code != 200:
            return_json = {
                "Message": "An error has occurred", 
                "Status Code": status_code
            }

            return jsonify(return_json)

        # Process the data
        x = postedData["x"]
        y = postedData["y"]

        x = int(x)
        y = int(y)

        result = x * y

        # Prepare the response
        return_map = {
            'Message': result, 
            'Status Code': 200
        }
        
        # Return the response
        return jsonify(return_map)

class Divide(Resource):
    def post(self):
        # Get the posted data
        postedData = request.get_json()

        # Validate the posted data
        status_code = checkPostedData(postedData, "divide")

        # Handle validation errors
        if status_code != 200:
            return_json = {
                "Message": "An error has occurred", 
                "Status Code": status_code
            }

            return jsonify(return_json)

        # Process the data
        x = postedData["x"]
        y = postedData["y"]

        x = int(x)
        y = int(y)

        result = x / y

        # Prepare the response
        return_map = {
            'Message': result, 
            'Status Code': 200
        }
        
        # Return the response
        return jsonify(return_map)

api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/divide")
api.add_resource(Visit, "/hello")

@app.route('/')
def hello_world():
    return "Hello world!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)