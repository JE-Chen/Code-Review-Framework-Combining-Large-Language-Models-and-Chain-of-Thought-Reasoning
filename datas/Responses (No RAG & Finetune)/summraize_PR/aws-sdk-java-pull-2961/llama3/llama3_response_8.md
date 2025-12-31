**Pull Request Summary**

**Issue:** None mentioned

**Description:** The author proposes a change to the default thread pool implementation in `AwsAsyncClientBuilder` to prevent unnecessary thread occupancy and memory leaks. The current implementation using `Executors.newFixedThreadPool` is replaced with a `ThreadPoolExecutor` that uses a `LinkedBlockingQueue` to manage tasks.

**Change:**

* The `defaultExecutor` method now returns a `ThreadPoolExecutor` instance with the following configuration:
	+ Core pool size: 0 (meaning the pool will grow and shrink dynamically)
	+ Maximum pool size: `getClientConfiguration().getMaxConnections()`
	+ Keep-alive time: 60 seconds
	+ Task queue: `LinkedBlockingQueue<Runnable>`

**Motivation:** The author experienced a memory leak issue when transmitting large amounts of data to SQS using a fixed thread pool. This change aims to prevent similar issues by using a more flexible and dynamic thread pool.

**License:** The author confirms that the contribution can be used, modified, copied, and redistributed under the terms of the contributor's choice.