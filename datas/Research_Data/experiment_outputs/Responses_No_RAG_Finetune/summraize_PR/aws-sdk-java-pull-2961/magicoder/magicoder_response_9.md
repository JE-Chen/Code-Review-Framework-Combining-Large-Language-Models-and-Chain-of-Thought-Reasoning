Issue #: If available, replace this with the actual issue number.

In the case of fixedThreadPool, unnecessary thread occupancy and memory leak can occur. That's why I'm going to change the default thread pool implementation of AwsAsyncClientBuilder.

In my case, the thread did not end after the process of transmitting large amounts of data to SQS, resulting in a memory leak.

I'm proposing to use a ThreadPoolExecutor instead of FixedThreadPool. FixedThreadPool allows the task execution in a pool of threads. This can lead to unnecessary thread occupancy and memory leak if not properly managed.

By using a ThreadPoolExecutor, I can control the maximum number of threads and discard tasks that exceed the maximum limit. This should help to prevent memory leaks and unnecessary thread occupancy.

The changes proposed are:

```java
private ExecutorService defaultExecutor() {
            return new ThreadPoolExecutor(0, getClientConfiguration().getMaxConnections(), 60L, TimeUnit.SECONDS, new LinkedBlockingQueue<Runnable>());
        }
```