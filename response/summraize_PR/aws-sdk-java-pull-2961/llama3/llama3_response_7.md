**PR Summary:**

**Issue:** # (not provided)

**Description:** This pull request aims to fix a memory leak issue that occurs when using the `fixedThreadPool` implementation in `AwsAsyncClientBuilder`. The issue is caused by unnecessary thread occupancy and memory leaks when transmitting large amounts of data to SQS.

**Changes:**

* The `defaultExecutor()` method is modified to use a `ThreadPoolExecutor` instead of `Executors.newFixedThreadPool()`.
* The `ThreadPoolExecutor` is configured with a `LinkedBlockingQueue` as the work queue, a core pool size of 0, a maximum pool size equal to `getClientConfiguration().getMaxConnections()`, and a keep-alive time of 60 seconds.

**Justification:** The change is necessary to prevent memory leaks and unnecessary thread occupancy when using the `fixedThreadPool` implementation.

**License:** The contributor confirms that they grant the project maintainers the right to use, modify, copy, and redistribute this contribution under the terms of the project's choice.