# Code Review: FileAsyncRequestBody Modification

## Summary
The PR addresses a critical bug in the SDK where file modification errors during async file uploads weren't properly propagated to the user. The proposed solution is well-structured and correctly fixes the issues identified. However, I've identified a few opportunities for improvement to enhance clarity, maintainability, and error messaging.

## Key Improvements in the Current PR
1. **Corrected error propagation timing** - Validation now occurs before signaling the last bytes to the subscriber, ensuring errors are properly propagated before Netty cancels the subscription.
2. **Non-retryable exception type** - Changed from `IOException` to `SdkClientException`, which is appropriate for terminal errors.
3. **Consistent initial metadata capture** - Ensures the initial file state is captured at the start of the request, not per-part in splits.

## Areas for Improvement

### 1. Inconsistent Null Handling
The current implementation handles `null` values for `modifiedTimeAtStart` and `sizeAtStart` in both the builder and the subscription class. This creates duplication and potential inconsistencies.

**Problem**: 
- In `FileAsyncRequestBody`, `null` values are handled in the constructor
- In `FileSubscription`, `null` values are handled again (which could lead to duplicate file system operations)

**Better Approach**: Handle `null` values consistently in the builder and ensure they're never `null` in the final object. This avoids duplicate file system calls and simplifies the code.

### 2. Error Message Clarity
While the error messages are better than before, they're still missing the file path, which would be extremely helpful for debugging.

**Better Approach**: Include the file path in all error messages to immediately identify which file caused the problem.

### 3. Validation Logic Complexity
The `validateFileUnchangedAndSignalErrors` method has multiple return points, which can make it harder to follow.

**Better Approach**: Simplify the logic with early returns to improve readability.

## Revised Implementation

Here's my proposed improved implementation:

```java
// core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java

// Add to class fields
private final FileTime modifiedTimeAtStart;
private final Long sizeAtStart;

// In constructor
private FileAsyncRequestBody(DefaultBuilder builder) {
    // ... existing validation code ...
    this.modifiedTimeAtStart = getModifiedTimeAtStart(builder);
    this.sizeAtStart = getSizeAtStart(builder);
}

private FileTime getModifiedTimeAtStart(DefaultBuilder builder) {
    if (builder.modifiedTimeAtStart != null) {
        return builder.modifiedTimeAtStart;
    }
    try {
        return Files.getLastModifiedTime(path);
    } catch (IOException e) {
        log.debug(() -> "Failed to get last modified time for path " + path, e);
        return null;
    }
}

private Long getSizeAtStart(DefaultBuilder builder) {
    if (builder.sizeAtStart != null) {
        return builder.sizeAtStart;
    }
    try {
        return Files.size(path);
    } catch (IOException e) {
        log.debug(() -> "Failed to get file size for path " + path, e);
        return null;
    }
}

// In FileSubscription constructor
private FileSubscription(AsynchronousFileChannel inputChannel,
                        Subscriber<? super ByteBuffer> subscriber,
                        FileTime modifiedTimeAtStart, Long sizeAtStart) throws IOException {
    // ... existing code ...
    this.modifiedTimeAtStart = modifiedTimeAtStart;
    this.sizeAtStart = sizeAtStart;
}

// In validateFileUnchangedAndSignalErrors
private boolean validateFileUnchangedAndSignalErrors() {
    try {
        // Validate size
        if (sizeAtStart != null) {
            long sizeAtEnd = Files.size(path);
            if (sizeAtStart != sizeAtEnd) {
                signalOnError(SdkClientException.create(String.format(
                    "File size changed after reading started for file: %s. Initial size: %d. Current size: %d",
                    path, sizeAtStart, sizeAtEnd)));
                return false;
            }
        }

        // Validate remaining bytes
        if (remainingBytes.get() > 0) {
            signalOnError(SdkClientException.create(String.format(
                "Fewer bytes were read than were expected for file: %s. Was the file modified after reading started?",
                path)));
            return false;
        }

        // Validate last modified time
        if (modifiedTimeAtStart != null) {
            FileTime modifiedTimeAtEnd = Files.getLastModifiedTime(path);
            if (modifiedTimeAtStart.compareTo(modifiedTimeAtEnd) != 0) {
                signalOnError(SdkClientException.create(String.format(
                    "File last-modified time changed after reading started for file: %s. Initial modification time: %s. Current modification time: %s",
                    path, modifiedTimeAtStart, modifiedTimeAtEnd)));
                return false;
            }
        }
    } catch (NoSuchFileException e) {
        signalOnError(SdkClientException.create(String.format(
            "Unable to check file status after read for file: %s. Was the file deleted or were its permissions changed?",
            path), e));
        return false;
    } catch (IOException e) {
        signalOnError(SdkClientException.create(String.format(
            "Unable to check file status after read for file: %s. Error: %s",
            path, e.getMessage()), e));
        return false;
    }
    
    return true;
}
```

## Why This Approach Is Better

1. **Consistent Null Handling**:
   - The `getModifiedTimeAtStart()` and `getSizeAtStart()` methods handle the `null` case in one place
   - Eliminates duplicate file system calls and logic
   - Makes the code more maintainable and less error-prone

2. **Improved Error Messages**:
   - All error messages now include the file path, which is critical for debugging
   - Messages are more consistent and descriptive
   - Provides immediate context about which file caused the problem

3. **Simplified Validation Logic**:
   - The validation method now has a clear, linear flow with early returns
   - Easier to understand and maintain
   - Reduces cognitive load for future developers

4. **No Performance Impact**:
   - The file system operations are still only done once (when the `FileAsyncRequestBody` is constructed)
   - The changes don't affect the performance of the main read path

## Trade-offs and Risks

1. **Trade-off: Slightly More Code**
   - The solution adds a few lines of code but significantly improves clarity
   - The trade-off is worth it for the increased maintainability and debugging value

2. **Risk: Potential for File Not Found**
   - The error messages now include the file path, which could potentially expose sensitive paths
   - However, this is a necessary trade-off for debugging, and the file path is already logged in other parts of the SDK

## Test Coverage

The tests added in the PR are comprehensive and cover the main scenarios. I'd recommend adding one more test case to verify the file path appears in the error message:

```java
@Test
public void file_path_in_error_message() throws Exception {
    AsyncRequestBody asyncRequestBody = FileAsyncRequestBody.builder()
        .path(testFile)
        .build();
    
    ControllableSubscriber subscriber = new ControllableSubscriber();
    asyncRequestBody.subscribe(subscriber);
    
    // Modify the file to trigger the error
    Thread.sleep(1_000);
    Files.setLastModifiedTime(testFile, FileTime.from(Instant.now()));
    
    assertThatThrownBy(() -> subscriber.completed.get(5, TimeUnit.SECONDS))
        .hasCauseInstanceOf(SdkClientException.class)
        .hasMessageContaining("File last-modified time changed after reading started for file: " + testFile);
}
```

## Conclusion

The original PR makes important improvements to fix the critical bug. My proposed changes enhance the solution by:
1. Ensuring consistent null handling
2. Adding the file path to all error messages (critical for debugging)
3. Simplifying the validation logic for better readability

These changes don't introduce new complexity or performance overhead, and they significantly improve the developer experience when debugging file modification issues. The error messages will now provide immediate context about which file was modified, making it much easier for users to diagnose and fix issues in their applications.