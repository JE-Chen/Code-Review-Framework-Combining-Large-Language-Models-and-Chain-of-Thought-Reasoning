from flask import Flask, request, jsonify
import time

app = Flask(__name__)

USERS = []
REQUEST_LOG = []
LAST_RESULT = None


@app.route("/user", methods=["GET", "POST", "PUT", "DELETE"])
def user_handler():
    global LAST_RESULT

    if request.method == "POST":
        data = request.json or {}

        if "name" not in data or "age" not in data:
            return jsonify({"error": "missing fields"}), 400

        user = {
            "id": len(USERS) + 1,
            "name": data["name"],
            "age": data["age"],
            "active": True
        }

        USERS.append(user)

        REQUEST_LOG.append({
            "action": "create",
            "user": user["name"],
            "time": time.time()
        })

        LAST_RESULT = user

        return jsonify(user)

    elif request.method == "GET":
        min_age = request.args.get("min_age")

        result = USERS

        if min_age is not None:
            result = [u for u in result if u["age"] >= int(min_age)]

        result = sorted(result, key=lambda x: x["age"])

        LAST_RESULT = result

        return jsonify(result)

    elif request.method == "PUT":
        data = request.json or {}

        user_id = data.get("id")
        new_age = data.get("age")

        for u in USERS:
            if u["id"] == user_id:
                u["age"] = new_age

                REQUEST_LOG.append({
                    "action": "update",
                    "user": u["name"],
                    "time": time.time()
                })

                LAST_RESULT = u

                return jsonify(u)

        return jsonify({"error": "user not found"}), 404

    elif request.method == "DELETE":
        data = request.json or {}
        user_id = data.get("id")

        for u in USERS:
            if u["id"] == user_id:
                USERS.remove(u)

                REQUEST_LOG.append({
                    "action": "delete",
                    "user": u["name"],
                    "time": time.time()
                })

                LAST_RESULT = u

                return jsonify({"deleted": True})

        return jsonify({"error": "user not found"}), 404


@app.route("/doStuff", methods=["POST"])
def do_stuff():
    data = request.json or {}

    x = data.get("x", 0)
    y = data.get("y", 0)

    result = (x * 2 + y) / 3

    if result.is_integer():
        result = int(result)

    global LAST_RESULT
    LAST_RESULT = result

    return jsonify({"result": result})


@app.route("/debug/state", methods=["GET"])
def debug_state():
    return jsonify({
        "users": USERS,
        "log": REQUEST_LOG,
        "last": LAST_RESULT
    })


@app.route("/stats", methods=["GET"])
def stats():
    create_count = len([x for x in REQUEST_LOG if x["action"] == "create"])
    update_count = len([x for x in REQUEST_LOG if x["action"] == "update"])
    delete_count = len([x for x in REQUEST_LOG if x["action"] == "delete"])

    text = (
        "{"
        + '"creates": ' + str(create_count) + ", "
        + '"updates": ' + str(update_count) + ", "
        + '"deletes": ' + str(delete_count)
        + "}"
    )

    return app.response_class(text, mimetype="application/json")


@app.route("/reset", methods=["GET"])
def reset():
    USERS.clear()
    REQUEST_LOG.clear()

    global LAST_RESULT
    LAST_RESULT = None

    return "reset done"




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
