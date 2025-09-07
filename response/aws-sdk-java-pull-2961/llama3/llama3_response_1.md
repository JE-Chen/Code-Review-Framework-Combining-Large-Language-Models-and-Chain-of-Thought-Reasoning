**PR Summary:**

This pull request (PR) aims to fix a potential memory leak issue in the `AwsAsyncClientBuilder` class. The default thread pool implementation has been changed from `Executors.newFixedThreadPool` to a `ThreadPoolExecutor` with a `LinkedBlockingQueue`.

**Problem:**

The previous implementation using `newFixedThreadPool` could lead to unnecessary thread occupancy and memory leaks, particularly when dealing with large amounts of data transmission to SQS.

**Change:**

The new implementation uses a `ThreadPoolExecutor` with a `LinkedBlockingQueue` to manage the thread pool. This change introduces the following benefits:

* The `ThreadPoolExecutor` allows for more flexible thread pool management, including the ability to reject new tasks when the pool is saturated.
* The `LinkedBlockingQueue` provides a bounded queue that prevents the thread pool from growing indefinitely.

**Key Changes:**

* `Executors.newFixedThreadPool` replaced with `new ThreadPoolExecutor(0, getClientConfiguration().getMaxConnections(), 60L, TimeUnit.SECONDS, new LinkedBlockingQueue<Runnable>())`
* Introduction of `LinkedBlockingQueue` to manage the thread pool

**PR Status:**

The PR includes a confirmation that the contributor grants permission for the PR to be used, modified,