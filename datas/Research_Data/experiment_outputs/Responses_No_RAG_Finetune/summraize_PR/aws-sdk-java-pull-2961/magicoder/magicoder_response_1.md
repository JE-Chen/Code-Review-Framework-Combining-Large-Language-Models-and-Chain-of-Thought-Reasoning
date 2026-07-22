Issue #: 

In the case of fixedThreadPool, unnecessary thread occupancy and memory leak can occur. That's why I'm going to change the default thread pool implementation of AwsAsyncClientBuilder.

In my case, the thread did not end after the process of transmitting large amounts of data to SQS, resulting in a memory leak.

A new ThreadPoolExecutor implementation is used, with a queue to hold requests that can't be processed immediately. The core pool size is set to 0, to allow the queue to be used for requests. The maximum pool size is set to the maximum connections configured for the client. The keep-alive time is set to 60 seconds. This should help to avoid unnecessary thread occupancy and memory leaks.

This change will allow the thread pool to be more efficient and provide better performance in dealing with a large amount of data transmission to SQS.