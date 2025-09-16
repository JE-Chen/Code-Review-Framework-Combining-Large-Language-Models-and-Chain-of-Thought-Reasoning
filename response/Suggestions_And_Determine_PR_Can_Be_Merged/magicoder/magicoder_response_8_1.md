Recommend Merge

This PR is addressing several issues related to file modification detection in AWS SDK for Java v2. The changes are substantial and should be merged to ensure the robustness of the file modification detection logic in the SDK. 

The issues are:

1. Exceptions signaled when file modification are detected are not propagated.
2. Exceptions are IOExceptions which are retryable. 
3. File modifications between retry attempt or different parts (from split) are not detected.

These issues are crucial to ensure that file modification exceptions are correctly propagated and retried by the SDK. 

The code diff is clean and logical, covering all the modifications required. It includes a comprehensive set of tests, ensuring that the changes do not introduce regressions. The PR also includes a changelog entry, and the code is released under the Apache 2 license.

The cognitive complexity of the `FileAsyncRequestBody` class is relatively low (15/15), making it easy to understand and maintain.

The issue of "public" modifier is also addressed, which is a common best practice in Java. 

However, the use of `Thread.sleep()` should be avoided in unit tests because it can make the tests brittle and hard to maintain. This issue is also addressed, with the use of `Thread.sleep()` replaced with a `TimeUnit.SECONDS.sleep(5)` call.

The remaining issues (Issue1 and Issue3) can be addressed in future if they are encountered in the SDK development.