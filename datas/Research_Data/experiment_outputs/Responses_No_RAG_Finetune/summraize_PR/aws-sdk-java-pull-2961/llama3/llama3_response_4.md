**GitHub Pull Request Summary**

**Issue #:** Not specified

**Description:** This pull request aims to address a memory leak issue in the `AwsAsyncClientBuilder` class. The default thread pool implementation is changed from `Executors.newFixedThreadPool` to `ThreadPoolExecutor` to prevent unnecessary thread occupancy and memory leaks.

**Changes:**

* The `defaultExecutor()` method now returns a `ThreadPoolExecutor` instance instead of a fixed thread pool.
* The `ThreadPoolExecutor` is configured with:
	+ 0 initial threads (allowing the pool to dynamically adjust its size)
	+ A maximum of `getClientConfiguration().getMaxConnections()` threads
	+ A keep-alive time of 60 seconds
	+ A `LinkedBlockingQueue` as the task queue

**Context:** The author experienced a memory leak issue when transmitting large amounts of data to SQS, which led to this change. The new implementation should prevent similar issues in the future.