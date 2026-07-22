This Github PR addresses an issue related to memory leakage in the AWS Java SDK, specifically in the Async client builder. In the case of fixedThreadPool, unnecessary thread occupancy and memory leak can occur. The PR suggests changing the default thread pool implementation of AwsAsyncClientBuilder to a ThreadPoolExecutor with a LinkedBlockingQueue to prevent memory leaks in the case of transmitting large amounts of data to AWS SQS.

This PR includes the following changes:

- The `AwsAsyncClientBuilder` now uses a `ThreadPoolExecutor` for executing tasks instead of a fixed thread pool.
- The `ThreadPoolExecutor` has a `LinkedBlockingQueue` as its work queue, which allows tasks to be submitted even when all threads are busy.
- The `ThreadPoolExecutor` has a default of 0 core threads, which means it will only create a thread to execute tasks when necessary, and will not have idle threads.
- The `ThreadPoolExecutor` has a maximum pool size equal to the maximum connections allowed by the client configuration.
- The `ThreadPoolExecutor` has a thread timeout of 60 seconds. This