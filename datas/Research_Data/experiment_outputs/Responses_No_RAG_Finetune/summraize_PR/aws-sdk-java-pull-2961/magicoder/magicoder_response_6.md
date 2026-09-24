Issue #, if available:

In the case of fixedThreadPool, unnecessary thread occupancy and memory leak can occur. That's why I'm going to change the default thread pool implementation of AwsAsyncClientBuilder.

In my case, the thread did not end after the process of transmitting large amounts of data to SQS, resulting in a memory leak.

Description of changes:

```java
private ExecutorService defaultExecutor() {
    return new ThreadPoolExecutor(0, getClientConfiguration().getMaxConnections(), 60L, TimeUnit.SECONDS, new LinkedBlockingQueue<Runnable>());
}
```

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice."