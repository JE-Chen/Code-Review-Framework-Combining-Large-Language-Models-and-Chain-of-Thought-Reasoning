Issue #: The issue number is not provided in the PR description.

In the case of fixedThreadPool, unnecessary thread occupancy and memory leak can occur. That's why I'm going to change the default thread pool implementation of AwsAsyncClientBuilder.

In my case, the thread did not end after the process of transmitting large amounts of data to SQS, resulting in a memory leak.

With this pull request, I'm creating a new thread pool that has a maximum number of threads equal to the maximum connections allowed by the client configuration. The threads in the pool will be idle until they are needed, and will then be reused when they are no longer needed. This should prevent memory leaks and unnecessary thread occupancy.

The `LinkedBlockingQueue` is used as the blocking queue for the thread pool executor. It ensures that requests are processed in the order they arrive, which should prevent any potential issues with out-of-order processing.

I have provided a description of the changes in the body of the PR, explaining the reasons behind the changes.

By submitting this pull request, I confirm that you can use