from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello world!"

@app.route('/hellothere')
def hi_there_everyone():
    return "General Kenobi!!"

@app.route('/add_two_nums', methods = ["POST"])
def add_two_nums():
    # Get x and y from post data
    data_dictionary = request.get_json()
    
    x = data_dictionary["x"]
    y = data_dictionary["y"]

    # Add the numbers
    z = x + y

    # Prepare JSON
    return_json = {
        'z': z
    }

    # Return JSON with 200 status code
    return jsonify(return_json), 200

if __name__ == "__main__":
    app.run()