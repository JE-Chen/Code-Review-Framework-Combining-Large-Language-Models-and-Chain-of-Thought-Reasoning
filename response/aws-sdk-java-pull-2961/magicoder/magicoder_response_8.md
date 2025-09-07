
PR #12345: Implementing a thread pool for AwsAsyncClientBuilder

ISSUE: #56789

Summary:
Replacing the fixedThreadPool implementation with a custom ThreadPoolExecutor. 

Background:
In the case of fixedThreadPool, unnecessary thread occupancy and memory leak can occur. That's why I'm going to change the default thread pool implementation of AwsAsyncClientBuilder.

The issue was that the threads didn't end after transmitting large amounts of data to SQS, resulting in a memory leak.

Changes:
In the method `defaultExecutor()`, I replaced the `Executors.newFixedThreadPool()` with a custom `ThreadPoolExecutor` implementation. This new implementation has a custom queue (`LinkedBlockingQueue`) and a custom rejected execution handler.

In this way, I ensure that:

1. The maximum thread count doesn't exceed the configured limit.
2. There's no unnecessary thread occupancy.
3. Tasks that are rejected due