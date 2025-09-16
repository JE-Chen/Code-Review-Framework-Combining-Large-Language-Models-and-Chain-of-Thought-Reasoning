Verdict: Merge with Changes

Reasoning:
- The PR addresses three separate issues and is well-tested.
- However, the codebase could be improved. For instance, the cognitive complexity of the `FileAsyncRequestBody` class is high (21), and the JUnit5 test classes and methods should have default package visibility. The use of `Thread.sleep()` in the test class is not recommended in tests.

Action Items:
- The cognitive complexity of the `FileAsyncRequestBody` class should be reduced.
- The JUnit5 test classes and methods should have default package visibility.
- The use of `Thread.sleep()` in the test class should be avoided.