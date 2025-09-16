Verdict: Do Not Merge

Reasoning:
- High cognitive complexity (21)
- Test visibility issues
- `Thread.sleep` usage in tests

Action Items:
- Refactor the `FileAsyncRequestBody::subscribe` method to reduce its complexity
- Reduce the visibility of test classes and methods to default package
- Avoid `Thread.sleep` in tests and replace it with appropriate testing techniques (like mocking or asserting on timestamps)
- If the PR is ready to merge, merge it after addressing these issues.