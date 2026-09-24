**Pull Request Summary**

**Issue**: # (not specified)
**Description**: This pull request aims to fix a potential memory leak issue in the `AwsAsyncClientBuilder` class by changing the default thread pool implementation from `fixedThreadPool` to a more flexible and leak-preventing `ThreadPoolExecutor`.

**Changes**:

* The `defaultExecutor()` method now returns a `ThreadPoolExecutor` with the following configuration:
	+ Core pool size: 0 (allowing the pool to dynamically adjust to the number of tasks)
	+ Maximum pool size: `getClientConfiguration().getMaxConnections()` (configurable via the client configuration)
	+ Keep-alive time: 60 seconds
	+ Queue: a `LinkedBlockingQueue` to prevent memory leaks
* The `fixedThreadPool` implementation, which can lead to unnecessary thread occupancy and memory leaks, is replaced with the more flexible `ThreadPoolExecutor`.

**Impact**: This change should help prevent memory leaks and improve the overall performance of the `AwsAsyncClientBuilder` class, particularly when dealing with large amounts of data transmission to SQS.