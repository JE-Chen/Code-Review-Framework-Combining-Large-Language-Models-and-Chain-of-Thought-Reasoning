### Code Smell Type:
Long Method

### Problem Location:
`MainWindow.add_user`
`MainWindow.delete_user`

### Detailed Explanation:
The `add_user` and `delete_user` methods contain multiple conditional checks and operations, leading to a long method that is difficult to read and understand. This makes the code harder to maintain and extend.

### Improvement Suggestions:
Refactor these methods into smaller, more focused functions. For example, extract validation logic into separate methods and handle UI updates separately.

```python
def validate_input(self):
    name = self.nameInput.text()
    age_text = self.txtAge.text()
    
    if name == "" or age_text == "":
        return False, "Missing input"
    
    try:
        age = int(age_text)
    except ValueError:
        return False, "Invalid age"
    
    if age < 0:
        return False, "Age cannot be negative"
    
    return True, None

def add_user(self):
    valid, error_message = self.validate_input()
    if not valid:
        self.lblStatus.setText(error_message)
        return
    
    name, age_text = self.nameInput.text(), self.txtAge.text()
    age = int(age_text)
    
    user = {"name": name, "age": age}
    self.users.append(user)
    time.sleep(0.3)
    self.output.append(f"Added: {name}, {age}")
    self.last_action = "add"
    self.lblStatus.setText(f"Total users: {len(self.users)}")

def delete_user(self):
    if len(self.users) == 0:
        self.lblStatus.setText("No users to delete")
        return
    
    user = self.users.pop()
    time.sleep(0.2)
    self.output.append(f"Deleted: {user['name']}")
    self.last_action = "delete"
    self.lblStatus.setText(f"Total users: {len(self.users)}")
```

### Priority Level:
High

---

### Code Smell Type:
Magic Numbers

### Problem Location:
`time.sleep(0.3)` in `add_user`
`time.sleep(0.2)` in `delete_user`

### Detailed Explanation:
Using hardcoded values like `0.3` and `0.2` without explanation can make the code hard to understand and modify. Magic numbers should be replaced with named constants.

### Improvement Suggestions:
Define constants at the beginning of the file or within the appropriate class.

```python
ADDITION_DELAY = 0.3
DELETION_DELAY = 0.2
```

Then use these constants in your code:

```python
time.sleep(ADDITION_DELAY)
```

### Priority Level:
Low

---

### Code Smell Type:
Redundant Code

### Problem Location:
Both `add_user` and `delete_user` update the status label after performing their actions.

### Detailed Explanation:
Updating the status label is repeated in both methods. This redundancy can lead to inconsistencies if one method changes but the other does not.

### Improvement Suggestions:
Create a helper method to update the status label.

```python
def update_status(self, message, color="blue"):
    self.lblStatus.setText(message)
    self.lblStatus.setStyleSheet(f"color: {color};")
```

Then call this method from both `add_user` and `delete_user`.

```python
def add_user(self):
    # ...
    self.update_status(f"Total users: {len(self.users)}", "green")
```

### Priority Level:
Medium

---