Issue #: None provided

In this PR, the author is proposing a change to the `AwsAsyncClientBuilder` class in the AWS SDK for Java. The change revolves around replacing the `Executors.newFixedThreadPool` with a `ThreadPoolExecutor` with a custom queue (`LinkedBlockingQueue`).

The motivation behind this change stems from the problem of memory leaks and excessive thread occupancy that was experienced when using the `Executors.newFixedThreadPool` with large amounts of data. By using a custom `ThreadPoolExecutor` with a custom queue, the author hopes to mitigate these issues.

In the `defaultExecutor` method, the `corePoolSize`, `maximumPoolSize`, `keepAliveTime`, `TimeUnit`, and `workQueue` parameters are provided new values:

- `corePoolSize` and `maximumPoolSize` are set to `0` and `getClientConfiguration().getMaxConnections()`, respectively, so that the pool does not pre-start any threads.
- `keepAliveTime` is set to `