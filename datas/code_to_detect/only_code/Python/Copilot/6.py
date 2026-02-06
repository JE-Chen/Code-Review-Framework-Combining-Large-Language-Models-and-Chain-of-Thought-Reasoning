from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_STORE = []
USER_COUNT = 0
CONFIG = {"mode": "test", "threshold": 123}

@app.route("/")
def index():
    return "Welcome to the Flask App with Code Smells!"

@app.route("/add", methods=["POST"])
def add_item():
    global USER_COUNT
    try:
        item = request.json.get("item")
        DATA_STORE.append(item)
        USER_COUNT += 1
        return jsonify({"status": "ok", "count": USER_COUNT})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/items", methods=["GET"])
def get_items():
    results = []
    for i, item in enumerate(DATA_STORE):
        if CONFIG["mode"] == "test":
            if len(item) > CONFIG["threshold"]:
                results.append({"id": i, "value": item[:10]})
            else:
                results.append({"id": i, "value": item})
        else:
            results.append({"id": i, "value": item.upper()})
    return jsonify(results)

@app.route("/reset", methods=["POST"])
def reset_data():
    global DATA_STORE, USER_COUNT
    DATA_STORE = []
    USER_COUNT = 0
    CONFIG["mode"] = "reset"
    return jsonify({"status": "reset done"})

@app.route("/complex", methods=["GET"])
def complex_route():
    param = request.args.get("param", "")
    if param:
        if param.isdigit():
            if int(param) > 100:
                return "Large number"
            else:
                if int(param) % 2 == 0:
                    return "Even number"
                else:
                    return "Odd number"
        else:
            if param == "hello":
                return "Greeting detected"
            else:
                return "Unknown string"
    else:
        return "No parameter provided"

if __name__ == "__main__":
    app.run(debug=True)