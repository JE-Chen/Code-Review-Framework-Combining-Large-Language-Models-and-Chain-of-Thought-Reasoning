# 一個「功能正常」的 Flask API
# 但設計品質是教科書級災難 🤮

from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# ❌ 全域可變狀態（Global Mutable State in Web App）
USERS = []
REQUEST_LOG = []
LAST_RESULT = None


# ❌ God Route：一個 endpoint 做 CRUD + 驗證 + 商業邏輯 + logging
@app.route("/user", methods=["GET", "POST", "PUT", "DELETE"])
def user_handler():
    global LAST_RESULT

    # ❌ Action by HTTP Method Switch（Controller 邏輯硬寫在一起）
    if request.method == "POST":
        data = request.json or {}

        # ❌ Inline Validation Logic（驗證邏輯散落在 route 中）
        if "name" not in data or "age" not in data:
            return jsonify({"error": "missing fields"}), 400

        user = {
            "id": len(USERS) + 1,  # ❌ ID 產生邏輯天真（Race condition 預備役）
            "name": data["name"],
            "age": data["age"],
            "active": True
        }

        USERS.append(user)

        # ❌ Side Effect Logging：偷偷改全域 log
        REQUEST_LOG.append({
            "action": "create",
            "user": user["name"],
            "time": time.time()
        })

        LAST_RESULT = user

        return jsonify(user)

    elif request.method == "GET":
        # ❌ Query Parameter Primitive Obsession
        min_age = request.args.get("min_age")

        result = USERS

        # ❌ 混合型別比較（String vs Int）
        if min_age is not None:
            result = [u for u in result if u["age"] >= int(min_age)]

        # ❌ 隱藏排序規則（Hidden Business Rule）
        result = sorted(result, key=lambda x: x["age"])

        LAST_RESULT = result

        return jsonify(result)

    elif request.method == "PUT":
        data = request.json or {}

        # ❌ 輸入完全信任（Missing Authorization / Validation）
        user_id = data.get("id")
        new_age = data.get("age")

        # ❌ O(n) 搜尋沒有任何抽象
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

        # ❌ 修改 list 同時遍歷（雖然這裡剛好不爆）
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


# ❌ RPC-style Endpoint：不像 REST 的 API 設計
@app.route("/doStuff", methods=["POST"])
def do_stuff():
    data = request.json or {}

    # ❌ Magic Parameter Names
    x = data.get("x", 0)
    y = data.get("y", 0)

    # ❌ 業務邏輯直接塞在 route
    result = (x * 2 + y) / 3

    # ❌ 不穩定回傳格式（有時 int，有時 float）
    if result.is_integer():
        result = int(result)

    global LAST_RESULT
    LAST_RESULT = result

    return jsonify({"result": result})


# ❌ Debug Endpoint 留在 production code
@app.route("/debug/state", methods=["GET"])
def debug_state():
    # ❌ 資安災難：整包內部狀態直接外洩
    return jsonify({
        "users": USERS,
        "log": REQUEST_LOG,
        "last": LAST_RESULT
    })


# ❌ Tight Coupling to Flask Global Objects
@app.route("/stats", methods=["GET"])
def stats():
    # ❌ 邏輯依賴 REQUEST_LOG 的內部結構
    create_count = len([x for x in REQUEST_LOG if x["action"] == "create"])
    update_count = len([x for x in REQUEST_LOG if x["action"] == "update"])
    delete_count = len([x for x in REQUEST_LOG if x["action"] == "delete"])

    # ❌ Hand-built JSON（不用 jsonify）
    text = (
        "{"
        + '"creates": ' + str(create_count) + ", "
        + '"updates": ' + str(update_count) + ", "
        + '"deletes": ' + str(delete_count)
        + "}"
    )

    return app.response_class(text, mimetype="application/json")


# ❌ 非 RESTful 的副作用 GET
@app.route("/reset", methods=["GET"])
def reset():
    USERS.clear()
    REQUEST_LOG.clear()

    global LAST_RESULT
    LAST_RESULT = None

    return "reset done"


# ❌ Blueprint 完全不用（Monolithic App）
# ❌ 沒有 config class、沒有 service layer、沒有 repository layer
# ❌ 完全不可測試的結構


if __name__ == "__main__":
    # ❌ Hard-coded Server Config
    app.run(host="0.0.0.0", port=5000, debug=True)
