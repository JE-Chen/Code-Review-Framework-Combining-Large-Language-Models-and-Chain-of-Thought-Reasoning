**GitHub PR Summary**

**Issue:** # (not specified)

**Description:** The author is changing the default thread pool implementation in `AwsAsyncClientBuilder` to prevent unnecessary thread occupancy and memory leaks.

**Problem:** In the case of fixed thread pool, threads were not being released after completing tasks, resulting in a memory leak when transmitting large amounts of data to SQS.

**Change:** The author is replacing the `Executors.newFixedThreadPool()` method with a `ThreadPoolExecutor` instance, which allows for more flexible configuration and better management of threads.

**Code Change:** The `defaultExecutor()` method is modified to return a `ThreadPoolExecutor` instance with the following settings:

* Initial pool size: 0 (meaning the pool will grow as needed)
* Maximum pool size: `getClientConfiguration().getMaxConnections()`
* Keep-alive time: 60 seconds
* Queue type: `LinkedBlockingQueue<Runnable>()`

**License:** The author grants permission for the contribution to be used, modified, copied, and redistributed under the terms of the contributor's choice.