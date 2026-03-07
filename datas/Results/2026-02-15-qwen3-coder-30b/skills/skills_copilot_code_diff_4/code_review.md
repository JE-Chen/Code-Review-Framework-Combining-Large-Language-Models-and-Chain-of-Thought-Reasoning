### **Diff #1**

---

### **1. Summary**

- **Purpose**: This change introduces a new Python script (`sql_app.py`) that connects to an SQLite database and performs basic CRUD operations such as creating a table, inserting data, and querying it.
- **Scope**: The entire file is a single function performing multiple unrelated tasks without modularization.
- **Plain-Language Explanation**: This script sets up a simple database, stores two user records, retrieves them, and prints out matching entries — all within one confusingly named function.

---

### **2. Linting Issues**

- ❌ **Global Variable Usage**: Using global variables (`conn`, `cursorThing`) violates clean code principles and makes testing difficult.
  - *Suggested Fix*: Pass dependencies explicitly or use classes instead.
- ❌ **SQL Injection Vulnerability**: Concatenating strings directly into SQL queries exposes the app to injection attacks.
  - *Suggested Fix*: Use parameterized queries like `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
- ❌ **Unnecessary Complexity in Logic Flow**: Nested `if` statements make logic harder to follow.
  - *Suggested Fix*: Simplify conditionals using early returns or switch-like structures.
- ❌ **Poor Error Handling**: Broad exception catching suppresses errors silently.
  - *Suggested Fix*: Catch specific exceptions and log meaningful messages.

---

### **3. Code Smells**

- 🧼 **God Function Anti-Pattern**: One function handles connection setup, data insertion, query execution, and printing.
  - *Problem*: Hard to test, debug, and reuse.
  - *Improvement*: Break down functionality into smaller, focused functions.
- ⚠️ **Magic Strings/Numbers**: Hardcoded values like `"Alice"`, `"Bob"` reduce flexibility and clarity.
  - *Problem*: Changes require manual edits; not scalable.
  - *Improvement*: Externalize these into constants or configuration files.
- 🔁 **Duplicated Logic**: Repeated conditional checks on names could be abstracted into reusable logic.
  - *Problem*: Maintenance burden increases with more users.
  - *Improvement*: Create helper functions or mapping dictionaries.
- 📦 **Tight Coupling**: Direct reliance on hardcoded DB path and table schema limits portability.
  - *Problem*: Difficult to adapt to other databases or schemas.
  - *Improvement*: Abstract database access via a class or ORM layer.

---