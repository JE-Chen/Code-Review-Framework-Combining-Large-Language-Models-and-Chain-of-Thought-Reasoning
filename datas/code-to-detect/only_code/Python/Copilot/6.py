# Flask 範例程式碼：能執行但充滿程式碼異味
# 程式碼異味包含：全域變數濫用、路由混亂、命名不清楚、錯誤處理不足、過度複雜邏輯

from flask import Flask, request, jsonify

app = Flask(__name__)

# 全域變數濫用
DATA_STORE = []
USER_COUNT = 0
CONFIG = {"mode": "test", "threshold": 123}  # 魔法數字

@app.route("/")
def index():
    # 過度簡化的首頁，沒有明確用途
    return "Welcome to the Flask App with Code Smells!"

@app.route("/add", methods=["POST"])
def add_item():
    global USER_COUNT
    try:
        # 沒有驗證輸入資料
        item = request.json.get("item")
        DATA_STORE.append(item)
        USER_COUNT += 1
        return jsonify({"status": "ok", "count": USER_COUNT})
    except Exception as e:
        # 過度廣泛的例外攔截
        return jsonify({"error": str(e)})

@app.route("/items", methods=["GET"])
def get_items():
    # 過度複雜的邏輯，硬塞在一個函式裡
    results = []
    for i, item in enumerate(DATA_STORE):
        if CONFIG["mode"] == "test":
            if len(item) > CONFIG["threshold"]:
                results.append({"id": i, "value": item[:10]})  # 魔法數字 10
            else:
                results.append({"id": i, "value": item})
        else:
            results.append({"id": i, "value": item.upper()})
    return jsonify(results)

@app.route("/reset", methods=["POST"])
def reset_data():
    # 無意義的重設函式
    global DATA_STORE, USER_COUNT
    DATA_STORE = []
    USER_COUNT = 0
    CONFIG["mode"] = "reset"
    return jsonify({"status": "reset done"})

@app.route("/complex", methods=["GET"])
def complex_route():
    # 過度巢狀的 if-else
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
    # Debug 模式硬編碼開啟
    app.run(debug=True)