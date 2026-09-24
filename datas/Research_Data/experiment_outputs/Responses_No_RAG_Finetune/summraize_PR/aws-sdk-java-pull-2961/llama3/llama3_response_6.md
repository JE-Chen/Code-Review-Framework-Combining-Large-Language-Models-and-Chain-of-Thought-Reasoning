**Pull Request Summary:**

* **Issue:** FixedThreadPool can cause unnecessary thread occupancy and memory leaks in the AwsAsyncClientBuilder.
* **Problem:** In the case of transmitting large amounts of data to SQS, the thread did not end, resulting in a memory leak.
* **Change:** The default thread pool implementation in AwsAsyncClientBuilder has been changed from `Executors.newFixedThreadPool` to `ThreadPoolExecutor` with a `LinkedBlockingQueue`.
* **Code Change:** The `defaultExecutor` method now returns a `ThreadPoolExecutor` with:
	+ Core pool size: 0 (meaning it will create new threads as needed)
	+ Maximum pool size: `getClientConfiguration().getMaxConnections`
	+ Keep alive time: 60 seconds
	+ Thread queue: `LinkedBlockingQueue<Runnable>`
* **License:** The contributor has confirmed that they grant the right to use, modify, copy, and redistribute this contribution under the terms of the project's choice.

**Review Notes:**

* The change should help prevent memory leaks and unnecessary thread occupancy in the AwsAsyncClientBuilder.
* The use of a `ThreadPoolExecutor` with a `LinkedBlockingQueue` allows for more control over the thread pool's behavior.
* The keep alive time