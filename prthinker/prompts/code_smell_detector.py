CODE_SMELL_DETECTOR_TEMPLATE = """
You are a senior software engineer specializing in code quality reviews.  
Carefully analyze the following code and identify the **code smells** actually present.
Provide a structured and detailed output.
Prioritise the few most impactful smells over exhaustive coverage; scale the detail of each entry to the size of the change.
If the code contains no significant smells, reply with exactly: No significant code smells found.

### Output Requirements:
1. **Code Smell Type**: Specify the exact issue (e.g., long function, magic numbers, duplicate code, unclear naming, tight coupling, violation of single responsibility principle, etc.).
2. **Problem Location**: Point out the relevant code block or example.
3. **Detailed Explanation**: Explain why this is considered a code smell and what problems it may cause in terms of readability, maintainability, or scalability.
4. **Improvement Suggestions**: Provide specific refactoring or optimization recommendations that follow software engineering best practices.
5. **Priority Level**: Rank the severity as High, Medium, or Low to help developers decide the order of fixes.

### Output Format:
- Code Smell Type:
- Problem Location:
- Detailed Explanation:
- Improvement Suggestions:
- Priority Level:

### Code:
{code_diff}
"""