### PR Summary Template

#### Summary Rules
- **Key changes**: The script `data_analysis.py` has been added with functions and variables related to data analysis using pandas.
- **Impact scope**: This module affects the data processing and analysis aspects of the project.
- **Purpose of changes**: To create a script that performs basic data manipulation and statistical analysis.
- **Risks and considerations**: The use of global variables (`GLOBAL_DF`, `ANOTHER_GLOBAL`) may lead to unexpected side effects if the script is integrated into larger projects.
- **Items to confirm**:
  - Verify the accuracy of the data manipulation steps.
  - Confirm the robustness of error handling.
  - Ensure the output is as expected during different scenarios.

#### Code diff to review
```python
import pandas as pd
import random

GLOBAL_DF = None
ANOTHER_GLOBAL = "分析開始"

def functionThatDoesTooMuchAndIsNotClear():
    global GLOBAL_DF
    data = {
        "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "Age": [25, 30, 35, 40, 45],
        "Score": [88, 92, 95, 70, 60]
    }
    GLOBAL_DF = pd.DataFrame(data)

    GLOBAL_DF["ScorePlusRandom"] = GLOBAL_DF["Score"] + random.randint(0, 10)
    GLOBAL_DF["ScorePlusRandomAgain"] = GLOBAL_DF["Score"] + random.randint(0, 10)

    try:
        mean_age = GLOBAL_DF["Age"].mean()
        if mean_age > 20:
            if mean_age < 50:
                print("平均年齡在合理範圍:", mean_age)
            else:
                print("平均年齡過高:", mean_age)
        else:
            print("平均年齡過低:", mean_age)
    except Exception as e:
        print("我不管錯誤是什麼:", e)

    result = GLOBAL_DF.describe()
    print("描述統計結果如下：")
    print(result)

if __name__ == "__main__":
    print(ANOTHER_GLOBAL)
    functionThatDoesTooMuchAndIsNotClear()
```

### Review Points

1. **Readability & Consistency**
   - **Indentation and Formatting**: The code uses consistent indentation and spacing. However, the comment at the end of lines might be better formatted for readability.
   - **Comments**: Comments are minimal and could be more descriptive.

2. **Naming Conventions**
   - **Variable Names**: `GLOBAL_DF` and `ANOTHER_GLOBAL` are not very descriptive. Consider renaming them to something like `df` and `analysis_start_message`.
   - **Function Name**: `functionThatDoesTooMuchAndIsNotClear` is vague. A more descriptive name would help understand its purpose.

3. **Software Engineering Standards**
   - **Modularity**: The function `functionThatDoesTooMuchAndIsNotClear` does too much and could be split into smaller functions.
   - **Maintainability**: Global variables can lead to issues. Consider passing data through function parameters instead.

4. **Logic & Correctness**
   - **Boundary Conditions**: The conditional checks for mean age could be simplified.
   - **Exception Handling**: Catching all exceptions (`except Exception as e`) is generally discouraged. Specific exceptions should be caught where possible.

5. **Performance & Security**
   - **Performance**: Using global variables and random numbers within loops could impact performance.
   - **Security**: No obvious security issues identified, but always validate inputs if they come from external sources.

6. **Documentation & Testing**
   - **Comments**: More detailed comments explaining each step would be beneficial.
   - **Tests**: Unit tests for individual functions would improve confidence in the code's correctness.

### Recommendations

1. **Refactor Function**: Break down `functionThatDoesTooMuchAndIsNotClear` into smaller functions.
2. **Rename Variables**: Improve variable names to enhance readability.
3. **Specific Exceptions**: Catch specific exceptions rather than all exceptions.
4. **Avoid Global Variables**: Pass data through function parameters.
5. **Add Comments**: Document each step of the process.
6. **Unit Tests**: Write unit tests for individual functions.