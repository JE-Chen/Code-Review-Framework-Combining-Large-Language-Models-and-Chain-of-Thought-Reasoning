[Improvement Suggestions]
- Fix the issues with the validation of file modifications and signaling of exceptions.
- Implement a way to validate file modifications in the split case.
- Rework the test suite to account for these changes.

[Meets Requirements]
- Yes, the code follows the requirements.

[Summary: Merge Decision]
- Do not merge.

[Reason]
- The code does not meet the requirements of the pull request.

[Additional Notes]
- The code does not validate file modifications and does not signal exceptions correctly.
- There are tests that are failing due to these issues.
- The code does not handle file modifications correctly in the split case.