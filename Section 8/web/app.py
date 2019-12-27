from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

BANK_USERNAME = "BANK"
TRANSACTION_FEE = 1


app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.BankApi
users = db["Users"]

def userExists(username):
    if users.find({"Username": username}).cont() == 0:
        return False
    else:
        return True

def verifyPassword(username, password):
    if not userExists(username):
        return False

    hashed_password = users.find_one({"Username": username})[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_password) == hashed_password:
        return True
    else: 
        return False

def getBalance(username):
    cash = users.find({"Username": username})[0]["Own"]
    return cash

def getDebt(username):
    debt = users.find({"Username": username})[0]["Debt"]
    return debt

def generateReturnDictionary(status, message):
    return_json = {
        "Status Code": status, 
        "Message": message
    }
    return return_json

def verifyCredentials(username, password):
    """
    Returns a tuple consisting of the Error response JSON and a boolean indicating whether or not there were errors

    If the username and password are valid, it will return None and False
    If the username and password are not valid, it will return an error dictionary (with status code and message) and True
    """
    if not userExists(username):
        return generateReturnDictionary(401, "Invalid username"), True
    
    correct_password = verifyPassword(username, password)

    if not correct_password:
        return generateReturnDictionary(401, "Invalid password"), True

    return None, False

def updateBalance(username, balance):
    users.update({"Username": username},{"$set":{"Own": balance}})

def updateDebt(username, balance):
    users.update({"Username": username},{"$set":{"Debt": balance}})

class Register(Resource):
    def post(self):
        postedData = request.get_json
        print(postedData)
        username = postedData["username"]
        password = postedData["password"]

        if userExists(username):
            return_json = {
                "Status Code": 400, 
                "Message": "User already exists"
            }
            return jsonify(return_json)

        hashed_password = bcrypt.hashed_password(password.encode('utf8'), bcrypt.gensalt())

        users.insert({"Username": username, "Password": hashed_password, "Own": 0, "Debt": 0})

        return_json = {
            "Status Code": 200, 
            "Message": "Successfully registered"
        }

        return jsonify(return_json)

class Add(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]

        return_json, error = verifyCredentials(username, password)

        if error:
            return jsonify(return_json)

        if amount <= 0:
            return jsonify(generateReturnDictionary(400, "Amount must be greater than 0"))

        # Handle the transaction fee for the bank
        amount -= TRANSACTION_FEE
        bank_cash = getBalance(BANK_USERNAME)
        updateBalance(BANK_USERNAME, bank_cash + TRANSACTION_FEE)

        # Update the account balance
        cash = getBalance(username)
        updateBalance(username, cash + amount)

        # Return the result
        return jsonify(generateReturnDictionary(200, "Deposit completed successfully"))

class Transfer(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        target_account = postedData["targetAccount"]
        amount = postedData["amount"]

        return_json, error = verifyCredentials(username, password)

        if error:
            return jsonify(return_json)

        if amount <= 0:
            return jsonify(generateReturnDictionary(400, "Amount must be greater than 0"))

        cash = getBalance(username)

        if cash <= amount + TRANSACTION_FEE:
            return jsonify(generateReturnDictionary(400, "Insufficient funds"))

        if not userExists(target_account):
            return jsonify(generateReturnDictionary(400, "Target account does not exist"))

        updateBalance(BANK_USERNAME, getBalance(BANK_USERNAME) + TRANSACTION_FEE)
        updateBalance(username, getBalance(username) - amount)
        updateBalance(target_account, getBalance(target_account) + amount - TRANSACTION_FEE)

        return jsonify(generateReturnDictionary(200, "Amount transferred successfully"))

class Balance(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        return_json, error = verifyCredentials(username, password)

        if error:
            return jsonify(return_json)

        # Get the user data, but filter out/omit the password an _id fields
        return_json = users.find({
            "Username", username
        }, {
            "Password": 0, 
            "_id": 0
        })[0]

        return jsonify(return_json)

class TakeLoan(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]

        return_json, error = verifyCredentials(username, password)

        if error:
            return jsonify(return_json)

        if amount <= 0:
            return jsonify(generateReturnDictionary(400, "Amount must be greater than 0"))

        updateDebt(username, getDebt(username) + amount)
        updateBalance(username, getBalance(username) + amount)

        return jsonify(generateReturnDictionary(200, "Loan taken successfully"))

class PayLoan(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]

        return_json, error = verifyCredentials(username, password)

        if error:
            return jsonify(return_json)

        if amount <= 0:
            return jsonify(generateReturnDictionary(400, "Amount must be greater than 0"))

        if getBalance(username) < amount:
            return jsonify(generateReturnDictionary(400, "Insufficient Funds"))

        updateBalance(username, getBalance(username) - amount)
        updateDebt(username, getDebt(username) - amount)        

        return jsonify(generateReturnDictionary(200, "Loan paid successfully"))

api.add_resource(Register, "/register")
api.add_resource(Add, "/add")
api.add_resource(Transfer, "/transfer")
api.add_resource(Balance, "/balance")
api.add_resource(TakeLoan, "/take_loan")
api.add_resource(PayLoan, "/pay_loan")

if __name__ == "__main__":
    app.run(host = '0.0.0.0')