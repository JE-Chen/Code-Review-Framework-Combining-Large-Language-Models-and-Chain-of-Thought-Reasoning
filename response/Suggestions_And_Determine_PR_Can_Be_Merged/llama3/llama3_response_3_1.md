Conclusion
----------

Based on the provided PR, I recommend merging it into the main branch. The changes address three related issues:

1. Exceptions signaled when file modification are detected are not propagated.
2. Exceptions are IOExceptions which are retryable.
3. File modifications between retry attempt or different parts (from split) are not detected.

The modifications include:

* Changing the order of validation for file modifications when reading bytes, ensuring that the error is signaled before the subscriber (e.g., Netty) calls cancel.
* Changing the exceptions signaled from the retryable IOException to a generic SdkClientException.
* Capturing the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructed, ensuring that it stays consistent between retries/splits.

The testing section shows that new tests have been added to cover the behavior, and manual testing has been performed to verify the changes.

Improvement Suggestions
------------------------

1.  **Cognitive Complexity**: The `validateFileUnchangedAndSignalErrors()` method has a Cognitive Complexity of 21, which is above the recommended limit of 15. To reduce the complexity, consider breaking the method into smaller, more focused methods, each with a lower Cognitive Complexity.

    ```java
// Before
private boolean validateFileUnchangedAndSignalErrors() {
    try {
        long sizeAtEnd = Files.size(path);
        if (sizeAtStart!= sizeAtEnd) {
            signalOnError(SdkClientException.create("File size changed after reading started. Initial size: "
                    + sizeAtStart + ". Current size: " + sizeAtEnd));
            return false;
        }

        //...
    } catch (IOException e) {
        signalOnError(SdkClientException.create("Unable to check file status after read.", e));
        return false;
    }
    return true;
}

// After
private boolean validateFileSize() {
    try {
        long sizeAtEnd = Files.size(path);
        if (sizeAtStart!= sizeAtEnd) {
            signalOnError(SdkClientException.create("File size changed after reading started. Initial size: "
                    + sizeAtStart + ". Current size: " + sizeAtEnd));
            return false;
        }
    } catch (IOException e) {
        signalOnError(SdkClientException.create("Unable to check file status after read.", e));
        return false;
    }
    return true;
}

private boolean validateFileModificationTime() {
    try {
        FileTime modifiedTimeAtEnd = Files.getLastModifiedTime(path);
        if (modifiedTimeAtStart.compareTo(modifiedTimeAtEnd)!= 0) {
            signalOnError(SdkClientException.create("File last-modified time changed after reading started. "
                    + "Initial modification time: " + modifiedTimeAtStart + ". Current modification time: "
                    + modifiedTimeAtEnd));
            return false;
        }
    } catch (IOException e) {
        signalOnError(SdkClientException.create("Unable to check file status after read.", e));
        return false;
    }
    return true;
}

//...

private boolean validateFileUnchangedAndSignalErrors() {
    if (!validateFileSize() ||!validateFileModificationTime()) {
        return false;
    }
    return true;
}
```

2.  **JUnit5 Test Class Visibility**: The `FileAsyncRequestBodyTest` class has a visibility modifier of `public`, which is not necessary. Consider removing the `public` modifier to follow the JUnit5 convention.

    ```java
// Before
public class FileAsyncRequestBodyTest {
    //...
}

// After
class FileAsyncRequestBodyTest {
    //...
}
```

3.  **Thread.sleep() Usage**: The `FileAsyncRequestBodyTest` class uses `Thread.sleep()` in several test methods. Consider replacing it with a more reliable and efficient way to wait for the file to be updated, such as using a `CountDownLatch` or a `CompletableFuture`.

    ```java
// Before
@Test
public void changingFile_fileGetsTouched_failsBecauseUpdatedModificationTime() throws Exception {
    //...
    Thread.sleep(1_000); // Wait for 1 second so that we are definitely in a different second than when the file was created
    Files.setLastModifiedTime(testFile, FileTime.from(Instant.now()));
    //...
}

// After
@Test
public void changingFile_fileGetsTouched_failsBecauseUpdatedModificationTime() throws Exception {
    //...
    CountDownLatch latch = new CountDownLatch(1);
    ExecutorService executor = Executors.newSingleThreadExecutor();
    executor.submit(() -> {
        try {
            Thread.sleep(1_000); // Wait for 1 second
            Files.setLastModifiedTime(testFile, FileTime.from(Instant.now()));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            latch.countDown();
        }
    });
    latch.await();
    //...
}
```