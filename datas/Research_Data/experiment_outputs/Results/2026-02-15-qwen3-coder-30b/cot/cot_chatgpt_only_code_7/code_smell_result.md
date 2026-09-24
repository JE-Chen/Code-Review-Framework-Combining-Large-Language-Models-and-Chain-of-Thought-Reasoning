---

### **Code Smell Type:**  
**Blocking I/O in UI Thread**

### **Problem Location:**  
```python
time.sleep(0.3)
time.sleep(0.2)
```

### **Detailed Explanation:**  
Using `time.sleep()` in the UI thread blocks the entire application’s responsiveness. This causes the GUI to freeze during operations like adding or deleting users, which results in a poor user experience. In event-driven environments such as Qt applications, blocking calls are particularly harmful because they prevent the UI from updating or reacting to user input.

### **Improvement Suggestions:**  
Replace `time.sleep()` with non-blocking alternatives such as `QTimer.singleShot` or background threads using `QThread`. For example:
```python
QTimer.singleShot(300, lambda: self.output.append(...))
```
This allows asynchronous execution without freezing the interface.

### **Priority Level:**  
High

---

### **Code Smell Type:**  
**Magic Numbers / Strings**

### **Problem Location:**  
```python
self.lblStatus.setText("Missing input")
self.lblStatus.setText("Invalid age")
self.lblStatus.setText("Age cannot be negative")
self.lblStatus.setText("No users to delete")
self.lblStatus.setText(f"Total users: {len(self.users)}")
```

### **Detailed Explanation:**  
These hardcoded strings reduce readability and maintainability. If these messages need to change, developers must update them in multiple places. Also, there's no centralized way to manage localized or reusable text.

### **Improvement Suggestions:**  
Define constants or use a message manager module for consistent and maintainable status texts:
```python
MISSING_INPUT = "Missing input"
INVALID_AGE = "Invalid age"
NEGATIVE_AGE = "Age cannot be negative"
NO_USERS = "No users to delete"
TOTAL_USERS = "Total users: {}"
```

### **Priority Level:**  
Medium

---

### **Code Smell Type:**  
**Exception Handling with Bare `except:` Clause**

### **Problem Location:**  
```python
try:
    age = int(age_text)
except:
    self.lblStatus.setText("Invalid age")
    return
```

### **Detailed Explanation:**  
The bare `except:` clause catches all exceptions silently, including system exits and keyboard interrupts. It prevents proper debugging and can mask unexpected errors. This makes troubleshooting harder and increases risk of silent failures.

### **Improvement Suggestions:**  
Catch specific exceptions like `ValueError` when parsing integers:
```python
try:
    age = int(age_text)
except ValueError:
    self.lblStatus.setText("Invalid age")
    return
```

### **Priority Level:**  
High

---

### **Code Smell Type:**  
**Tight Coupling Between UI and Business Logic**

### **Problem Location:**  
In `add_user()` and `delete_user()`, direct access to widgets (`self.nameInput`, `self.txtAge`) and UI updates (`self.output.append`) occurs within business logic methods.

### **Detailed Explanation:**  
Mixing presentation logic with domain logic reduces modularity and testability. Refactoring would allow easier testing and future UI changes without touching core logic.

### **Improvement Suggestions:**  
Separate concerns by introducing a model layer that handles data and state independently of the UI. For instance:
- Move data manipulation into a separate class (`UserManager`)
- Pass signals or callbacks instead of directly modifying UI elements

### **Priority Level:**  
Medium

---

### **Code Smell Type:**  
**Lack of Input Validation Beyond Basic Checks**

### **Problem Location:**  
Validation only checks for empty fields and valid integer age.

### **Detailed Explanation:**  
There’s no check for maximum age limits, invalid characters in names, or whitespace trimming. This could lead to inconsistent data entry or UI glitches if malformed input slips through.

### **Improvement Suggestions:**  
Implement more robust input sanitization:
- Trim whitespace from inputs
- Enforce reasonable age ranges (e.g., 0–150)
- Validate string length and allowed character sets

### **Priority Level:**  
Medium

---

### **Code Smell Type:**  
**Global State Dependency (`app`, `window`) and Hardcoded Geometry**

### **Problem Location:**  
```python
app = QApplication(sys.argv)
...
self.setGeometry(100, 100, 500, 400)
```

### **Detailed Explanation:**  
The app initialization and fixed geometry make it hard to reuse or scale the component. These hardcoded values reduce flexibility and break portability across different screen sizes or platforms.

### **Improvement Suggestions:**  
Use dynamic layout managers, configuration files, or environment variables for sizing. Avoid hardcoding dimensions unless absolutely necessary.

### **Priority Level:**  
Low

---

### **Code Smell Type:**  
**Redundant Code in Status Updates**

### **Problem Location:**  
Multiple repeated lines in `refresh_status()` and `add_user()`/`delete_user()` regarding color styling and status text.

### **Detailed Explanation:**  
Repetition increases maintenance overhead. The same behavior appears in several places—this can cause inconsistencies if one part is updated but others aren’t.

### **Improvement Suggestions:**  
Create helper functions to encapsulate status setting logic:
```python
def set_status_message(message, color="blue"):
    self.lblStatus.setText(message)
    self.lblStatus.setStyleSheet(f"color: {color}; font-size: 14px;")
```

### **Priority Level:**  
Medium

---