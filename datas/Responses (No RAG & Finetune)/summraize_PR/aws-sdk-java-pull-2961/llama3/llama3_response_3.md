**Pull Request Summary**

**Issue:** # (not provided)

**Description:** This pull request aims to fix a memory leak and unnecessary thread occupancy issue in the `AwsAsyncClientBuilder` class. The default thread pool implementation will be changed from `Executors.newFixedThreadPool` to a `ThreadPoolExecutor` with a `LinkedBlockingQueue`.

**Changes:**

* The `defaultExecutor()` method now returns a `ThreadPoolExecutor` instance with the following configuration:
	+ Core pool size: 0
	+ Maximum pool size: `getClientConfiguration().getMaxConnections()`
	+ Keep-alive time: 60 seconds
	+ Queue: `LinkedBlockingQueue<Runnable>()`

**Reason for change:** The original implementation using `Executors.newFixedThreadPool` was causing a memory leak and unnecessary thread occupancy when transmitting large amounts of data to SQS.

**License:** The contributor confirms that the contribution can be used, modified, copied, and redistributed under the terms of the contributor's choice.