Issue #: @@ Issue Number @@

Summary:
The issue is that in the fixedThreadPool, the threads do not get recycled when they are no longer needed, leading to unnecessary thread occupancy and memory leak. To fix this, I am going to change the default thread pool implementation of AwsAsyncClientBuilder to a custom ThreadPoolExecutor.

Detailed description:

The existing fixedThreadPool uses a fixed number of threads and does not reuse them. This leads to a situation where the number of threads could be more than the maximum number of connections allowed by the service if the service is under heavy load. This could result in unnecessary thread occupancy and also a memory leak because the threads stay alive until the application ends, even though they are idle.

I am proposing to replace the existing fixed thread pool with a ThreadPoolExecutor which reuses threads, thereby reducing memory usage and avoiding unnecessary thread occupancy. The ThreadPoolExecutor will have a core size of 0, meaning it will not create any threads until there are pending tasks, and a maximum size of the maximum number of connections allowed by the service. It will also have a keep-