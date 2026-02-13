### Diff #1  
**Summary**  
The PR introduces a new file `bad_requests.py` with a complex function that performs multiple HTTP requests and error handling. The function is hard to understand, uses global variables, and has duplicated logic.  

---

### Linting Issues  
- **Formatting**: Missing spaces around operators and after commas.  
- **Global Variables**: Global variables (`GLOBAL_SESSION`, `ANOTHER_GLOBAL`) are not used in the function.  
- **Error Handling**: `except:` clause is used without `as` binding, which is not standard.  
- **Print Statements**: Poorly formatted and not structured for readability.  

---

### Code Smells  
- **Tight Coupling**: The function is tightly coupled with HTTP requests and error handling.  
- **Poor Naming**: `weirdVariableName` is unclear and not descriptive.  
- **Global State**: Global variables (`GLOBAL_SESSION`) are used without proper encapsulation.  
- **Duplication**: Error handling and request logic are repeated.  

---  
**Recommendations**:  
- Refactor the function into smaller, reusable methods.  
- Use local variables instead of global ones.  
- Enforce PEP8 formatting and proper error handling.