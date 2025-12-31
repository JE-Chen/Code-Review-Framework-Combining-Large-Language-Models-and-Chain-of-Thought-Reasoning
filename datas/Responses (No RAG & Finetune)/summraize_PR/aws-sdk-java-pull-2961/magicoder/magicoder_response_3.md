Issue number: #

Title: FixedThreadPool memory leak issue and unnecessary thread occupancy

In the mentioned PR, the author is addressing the issue of unnecessary thread occupancy and memory leak in the `fixedThreadPool`. To do this, they've made changes to the `AwsAsyncClientBuilder`, specifically the `defaultExecutor()` method.

The change is to use a `ThreadPoolExecutor` instead of a `FixedThreadPool`. A `ThreadPoolExecutor` is a class that allows the management of a group of threads. In this case, the ThreadPoolExecutor has been configured with a core pool size of 0, a maximum pool size of the maximum connections, and a keep alive time of 60 seconds. The queue used is a `LinkedBlockingQueue`, which means that tasks are stored in a queue until a thread is available.

This change results in a more efficient use of threads, as tasks are not immediately executed when submitted but stored in a queue until a thread becomes available. This should help to prevent unnecessary thread occupancy and memory leak in the case of large amounts of data transmission to SQS.
