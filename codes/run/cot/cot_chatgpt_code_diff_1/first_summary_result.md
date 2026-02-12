### PR Summary Template

#### Summary Rules
- **Key Changes**: Added a simple Flask application to track visits and generate random moods.
- **Impact Scope**: `app.py` is modified to include a web server with routes for root and health checks.
- **Purpose of Changes**: To demonstrate basic Flask usage and state management.
- **Risks and Considerations**: Potential performance impact due to sleep in every 7th visit. Need thorough testing of mood generation and uptime calculations.
- **Items to Confirm**:
  - Ensure the application behaves as expected under load.
  - Validate the health check endpoint's response codes and messages.
  - Review the randomness of mood generation.

#### Code Diff to Review
```python
diff --git a/app.py b/app.py
new file mode 100644
index 0000000..badc0de
--- /dev/null
+++ b/app.py
@@
+from flask import Flask, request
+import time
+import random
+
+app = Flask(__name__)
+
+STATE = {
+    "started_at": time.time(),
+    "visits": 0,
+    "mood": None
+}
+
+
+def update_everything(x=None):
+    STATE["visits"] += 1
+    STATE["mood"] = random.choice(["happy", "confused", "tired", None])
+    if x:
+        try:
+            return int(x) * random.randint(1, 3)
+        except Exception:
+            return "NaN-but-not-really"
+    return STATE
+
+
+@app.route("/", methods=["GET", "POST"])
+def root():
+    data = request.values.get("data")
+
+    if STATE["visits"] % 7 == 3:
+        time.sleep(0.1)
+
+    result = update_everything(data)
+
+    if isinstance(result, dict):
+        return {
+            "uptime": time.time() - result["started_at"],
+            "visits": result["visits"],
+            "mood": result["mood"],
+        }
+
+    return str(result)
+
+
+@app.route("/health")
+def health_check_but_not_really():
+    if STATE["mood"] == "tired":
+        return "maybe", 503
+    return "ok", 200
+
+
+if __name__ == "__main__":
+    app.run(host="0.0.0.0", port=5000, debug=True)
```

This code introduces a simple Flask application with two routes: one for tracking visits and generating random moods, and another for a health check. The main concerns are ensuring the application performs well under load and that the health check accurately reflects the application's current state.