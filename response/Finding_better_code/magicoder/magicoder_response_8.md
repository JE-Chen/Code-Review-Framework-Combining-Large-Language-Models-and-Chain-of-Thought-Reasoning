Sure, I'd be happy to review your proposed changes and provide feedback. Here's an improved version of your pull request:

```
> Surface errors from FileAsyncRequestBody when files are modified during request.
> 
> ## Motivation and Context
> This PR addresses three related issues:
> 
> 1. Exceptions signaled when file modification are detected are not propagated.
> 2. Exceptions are IOExceptions which are retryable.
> 3. File modifications between retry attempt or different parts (from split) are not detected.
> 
> We have logic in the [FileAsyncRequestBody](https://github.com/aws/aws-sdk-java-v2/blob/master/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java#L409) that detected changes in file modification time and signaled IOExceptions - but these were not being propagated.  
> 
> The `NettyRequestExecutor` (which, indirectly, is subscribed to the `FileAsyncRequestBody.FilePublisher`) calls `cancel` when Netty detects that it has read the full expected content-length (see logic [here](https://github.com/aws/aws-sdk-java-v2/blob/a4102def007a7b7a7e76efd30c7e07721dba25a1/http-clients/netty-nio-client/src/main/java/software/amazon/awssdk/http/nio/netty/internal/NettyRequestExecutor.java#L455)). Once `cancel` has been called, the Reactive Streams spec specifies that errors should no longer be signaled (and our code respects that). The check for file modification time changes is only done in `onComplete` which is only called after Netty cancels the subscription, meaning errors will never be propagated. The solution to this is to move the validation logic into the onComplete during read, specifically a check [here](https://github.com/aws/aws-sdk-java-v2/blob/master/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java#L341) _before_ the call to `signalOnNext` (which will cause Netty to call cancel).
> 
>   The second issue is that the exception raised is an IOException, which is considered retryable by default. File modification during request should be terminal.
> 
>   The third issue is that we were recording the initial modification time and file size when the Publisher is created - which is done per execution attempt / per part in split, so if the file is modified between attempts or between parts, it was not being detected.
> 
> ## Modifications
> There are three changes, which address each of the issues listed above.
> 
> 1. Change the order of validation for file modifications - when reading bytes, once we have read the full file, we validate that the file has not been modified _before_ calling onNext on the subscription.  This ensures that the error is signaled before the subscriber (eg Netty) calls cancel.
> 2. Change the exceptions signaled from the retryable IOException to a generic SdkClientException.
> 3. Capture the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructured, ensuring that it stays consistent between retries/splits.
> 
> ## Testing
> Added new tests to cover behavior.
> 
> Manual testing of behavior: **Behavior of putObject/uploadFile with different setups when file modified**:
> 
> Low level clients:
> 
> * S3AsyncClient (single/multi part, netty http client):  **Throws new exception**
> * S3AsyncClient (single/multi part, crt http client) - **Throws new exception**
> * S3CrtAsyncClient - **No Change in behavior** - No exception, request completes normally.
> 
> TransferManagers:
> 
> * Java TM (single/multi part): **Throws new exception**
> * CrtTM: **No change in behavior** - no exception, completes normally.
> 
> Example exception:
> 
> ```
> software.amazon.awssdk.core.exception.SdkClientException: Unable to execute HTTP request: File last-modified time changed after reading started. Initial modification time: 2025-09-05T19:20:46.540910708Z. Current modification time: 2025-09-05T19:20:47.981202736Z (SDK Attempt Count: 1)
> ```
> 
> ## Screenshots (if appropriate)
> ## Types of changes
> * [x]  Bug fix (non-breaking change which fixes an issue)
> * [ ]  New feature (non-breaking change which adds functionality)
> 
> ## Checklist
> * [x]  I have read the [CONTRIBUTING](https://github.com/aws/aws-sdk-java-v2/blob/master/CONTRIBUTING.md) document
> * [x]  Local run of `mvn install` succeeds
> * [x]  My code follows the code style of this project
> * [x]  My change requires a change to the Javadoc documentation
> * [x]  I have updated the Javadoc documentation accordingly
> * [x]  I have added tests to cover my changes
> * [x]  All new and existing tests passed
> * [x]  I have added a changelog entry. Adding a new entry must be accomplished by running the `scripts/new-change` script and following the instructions. Commit the new file created by the script in `.changes/next-release` with your changes.
> * [ ]  My change is to implement 1.11 parity feature and I have updated [LaunchChangelog](https://github.com/aws/aws-sdk-java-v2/blob/master/docs/LaunchChangelog.md)
> 
> ## License
> * [x]  I confirm that this pull request can be released under the Apache 2 license
```

Code diff:
```
diff --git a/.changes/next-release/bugfix-AWSSDKforJavav2-4bab915.json b/.changes/next-release/bugfix-AWSSDKforJavav2-4bab915.json
new file mode 100644
index 00000000000..e35f2176070
--- /dev/null
+++ b/.changes/next-release/bugfix-AWSSDKforJavav2-4bab915.json
@@ -0,0 +1,6 @@
+{
+    "type": "bugfix",
+    "category": "AWS SDK for Java v2",
+    "contributor": "",
+    "description": "Ensure that file modification exceptions in FileAsyncRequestBody are propogated correctly."
+}
diff --git a/.changes/next-release/bugfix-AWSSDKforJavav2-4bab915.json b/.changes/next-release/bugfix-AWSSDKforJavav2-4bab915.json
new file mode 100644
index 00000000000..38ca9cec61a
--- /dev/null
+++ b/.changes/next-release/bugfix-AWSSDKforJavav2-4bab915.json
@@ -0,0 +1,6 @@
+{
+    "type": "bugfix",
+    "category": "AWS SDK for Java v2",
+    "contributor": "",
+    "description": "Ensure that file modification exceptions in AsyncRequestBody#fromFile are propagated correctly."
+}
diff --git a/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java b/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java
index 2af70796f4e..59f8a4ca92d 100644
--- a/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java
+++ b/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java
@@ -36,6 +36,7 @@
 import software.amazon.awssdk.core.async.AsyncRequestBodySplitConfiguration;
 import software.amazon.awssdk.core.async.CloseableAsyncRequestBody;
 import software.amazon.awssdk.core.async.SdkPublisher;
+import software.amazon.awssdk.core.exception.SdkClientException;
 import software.amazon.awssdk.core.internal.util.Mimetype;
 import software.amazon.awssdk.core.internal.util.NoopSubscription;
 import software.amazon.awssdk.utils.Logger;
@@ -71,6 +72,8 @@ public final class FileAsyncRequestBody implements AsyncRequestBody {
     private final int chunkSizeInBytes;
     private final long position;
     private final long numBytesToRead;
+    private FileTime modifiedTimeAtStart;
+    private Long sizeAtStart;
 
     private FileAsyncRequestBody(DefaultBuilder builder) {
         this.path = builder.path;
@@ -79,6 +82,27 @@ private FileAsyncRequestBody(DefaultBuilder builder) {
         this.position = builder.position == null ? 0 : Validate.isNotNegative(builder.position, "position");
         this.numBytesToRead = builder.numBytesToRead == null ? fileLength - this.position :
                               Validate.isNotNegative(builder.numBytesToRead, "numBytesToRead");
+        if (builder.modifiedTimeAtStart != null) {
+            this.modifiedTimeAtStart = builder.modifiedTimeAtStart;
+        } else {
+            try {
+                this.modifiedTimeAtStart = Files.getLastModifiedTime(path);
+            } catch (IOException e) {
+                log.debug(() -> "Failed to get last modified time for path " + path, e);
+                this.modifiedTimeAtStart = null;
+            }
+        }
+
+        if (builder.sizeAtStart != null) {
+            this.sizeAtStart = builder.sizeAtStart;
+        } else {
+            try {
+                this.sizeAtStart = Files.size(path);
+            } catch (IOException e) {
+                log.debug(() -> "Failed to get file size for path " + path, e);
+                this.sizeAtStart = null;
+            }
+        }
     }
 
     @Override
@@ -112,6 +136,14 @@ public long numBytesToRead() {
         return numBytesToRead;
     }
 
+    public FileTime modifiedTimeAtStart() {
+        return modifiedTimeAtStart;
+    }
+
+    public Long sizeAtStart() {
+        return sizeAtStart;
+    }
+
     @Override
     public Optional<Long> contentLength() {
         return Optional.of(numBytesToRead);
@@ -131,7 +163,7 @@ public void subscribe(Subscriber<? super ByteBuffer> s) {
             // We need to synchronize here because the subscriber could call
             // request() from within onSubscribe which would potentially
             // trigger onNext before onSubscribe is finished.
-            Subscription subscription = new FileSubscription(channel, s);
+            Subscription subscription = new FileSubscription(channel, s, modifiedTimeAtStart, sizeAtStart);
 
             synchronized (subscription) {
                 s.onSubscribe(subscription);
@@ -203,6 +235,20 @@ public void completed(Integer result, ByteBuffer attachment) {
 
                             int readBytes = attachment.remaining();
                             currentPosition.addAndGet(readBytes);
-                            remainingBytes.addAndGet(-readBytes);
+                            long remaining = remainingBytes.addAndGet(-readBytes);
+
+                            // we need to validate the file is unchanged before providing the last bytes to subscriber
+                            // the subscriber (eg: NettyRequestExecutor) may cancel subscription once all expected bytes have
+                            // been received.  Validating here ensures errors are correctly signaled.
+                            if (remaining == 0) {
+                                closeFile();
+                                if (!validateFileUnchangedAndSignalErrors()) {
+                                    return;
+                                }
+                            }
 
                             signalOnNext(attachment);
 
-                            if (remainingBytes.get() == 0) {
-                                closeFile();
+                            if (remaining == 0) {
                                 signalOnComplete();
                             }
 
@@ -391,42 +470,49 @@ private void signalOnNext(ByteBuffer attachment) {
         }
 
         private void signalOnComplete() {
+            if (!validateFileUnchangedAndSignalErrors()) {
+                return;
+            }
+
+            synchronized (this) {
+                if (!done) {
+                    done = true;
+                    subscriber.onComplete();
+                }
+            }
+        }
+
+        private boolean validateFileUnchangedAndSignalErrors() {
             try {
                 long sizeAtEnd = Files.size(path);
                 if (sizeAtStart != sizeAtEnd) {
-                    signalOnError(new IOException("File size changed after reading started. Initial size: " + sizeAtStart + ". "
-                                                  + "Current size: " + sizeAtEnd));
-                    return;
+                    signalOnError(SdkClientException.create("File size changed after reading started. Initial size: "
+                                                         + sizeAtStart + ". Current size: " + sizeAtEnd));
+                    return false;
                 }
 
                 if (remainingBytes.get() > 0) {
-                    signalOnError(new IOException("Fewer bytes were read than were expected, was the file modified after "
-                                                  + "reading started?"));
-                    return;
+                    signalOnError(SdkClientException.create("Fewer bytes were read than were expected, was the file modified "
+                                                           + "after reading started?"));
+                    return false;
                 }
 
                 FileTime modifiedTimeAtEnd = Files.getLastModifiedTime(path);
                 if (modifiedTimeAtStart.compareTo(modifiedTimeAtEnd) != 0) {
-                    signalOnError(new IOException("File last-modified time changed after reading started. Initial modification "
-                                                  + "time: " + modifiedTimeAtStart + ". Current modification time: " +
-                                                  modifiedTimeAtEnd));
-                    return;
+                    signalOnError(SdkClientException.create("File last-modified time changed after reading started. "
+                                                            + "Initial modification time: " + modifiedTimeAtStart
+                                                            + ". Current modification time: " + modifiedTimeAtEnd));
+                    return false;
                 }
             } catch (NoSuchFileException e) {
-                signalOnError(new IOException("Unable to check file status after read. Was the file deleted or were its "
-                                              + "permissions changed?", e));
-                return;
+                signalOnError(SdkClientException.create("Unable to check file status after read. Was the file deleted"
+                                                        + " or were its permissions changed?", e));
+                return false;
             } catch (IOException e) {
-                signalOnError(new IOException("Unable to check file status after read.", e));
-                return;
-            }
-
-            synchronized (this) {
-                if (!done) {
-                    done = true;
-                    subscriber.onComplete();
-                }
+                signalOnError(SdkClientException.create("Unable to check file status after read.", e));
+                return false;
             }
+            return true;
         }
 
         private void signalOnError(Throwable t) {
diff --git a/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBodySplitHelper.java b/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBodySplitHelper.java
index 8cb7d28c662..6a9831ed726 100644
--- a/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBodySplitHelper.java
+++ b/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBodySplitHelper.java
@@ -17,6 +17,7 @@
 
 import java.nio.ByteBuffer;
 import java.nio.file.Path;
+import java.nio.file.attribute.FileTime;
 import java.util.Optional;
 import java.util.concurrent.atomic.AtomicBoolean;
 import java.util.concurrent.atomic.AtomicInteger;
@@ -53,6 +54,8 @@ public final class FileAsyncRequestBodySplitHelper {
 
     private AtomicInteger numAsyncRequestBodiesInFlight = new AtomicInteger(0);
     private AtomicInteger chunkIndex = new AtomicInteger(0);
+    private final FileTime modifiedTimeAtStart;
+    private final long sizeAtStart;
 
     public FileAsyncRequestBodySplitHelper(FileAsyncRequestBody asyncRequestBody,
                                            AsyncRequestBodySplitConfiguration splitConfiguration) {
@@ -70,6 +73,8 @@ public FileAsyncRequestBodySplitHelper(FileAsyncRequestBody asyncRequestBody,
                                splitConfiguration.bufferSizeInBytes();
         this.bufferPerAsyncRequestBody = Math.min(asyncRequestBody.chunkSizeInBytes(),
                                                   NumericUtils.saturatedCast(totalBufferSize));
+        this.modifiedTimeAtStart = asyncRequestBody.modifiedTimeAtStart();
+        this.sizeAtStart = asyncRequestBody.sizeAtStart();
     }
 
     public SdkPublisher<AsyncRequestBody> split() {
@@ -134,6 +139,8 @@ private AsyncRequestBody newFileAsyncRequestBody(SimplePublisher<AsyncRequestBod
                                                                         .position(position)
                                                                         .numBytesToRead(numBytesToReadForThisChunk)
                                                                         .chunkSizeInBytes(bufferPerAsyncRequestBody)
+                                                                        .modifiedTimeAtStart(modifiedTimeAtStart)
+                                                                        .sizeAtStart(sizeAtStart)
                                                                         .build();
         return new FileAsyncRequestBodyWrapper(fileAsyncRequestBody, simplePublisher);
     }
diff --git a/core/sdk-core/src/test/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBodyTest.java b/core/sdk-core/src/test/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBodyTest.java
index 4f20c77700e..5c2d4598963 100644
--- a/core/sdk-core/src/test/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBodyTest.java
+++ b/core/sdk-core/src/test/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBodyTest.java
@@ -17,6 +17,7 @@
 
 import static org.assertj.core.api.Assertions.assertThat;
 import static org.assertj.core.api.Assertions.assertThatThrownBy;
+import static org.junit.jupiter.api.Assertions.assertEquals;
 import static org.junit.jupiter.api.Assertions.assertTrue;
 import static software.amazon.awssdk.utils.FunctionalUtils.invokeSafely;
 
@@ -30,6 +31,8 @@
 import java.nio.file.Path;
 import java.nio.file.attribute.FileTime;
 import java.time.Instant;
+import java.util.ArrayList;
+import java.util.List;
 import java.util.concurrent.CompletableFuture;
 import java.util.concurrent.Semaphore;
 import java.util.concurrent.ThreadLocalRandom;
@@ -40,6 +43,7 @@
 import org.reactivestreams.Subscriber;
 import org.reactivestreams.Subscription;
 import software.amazon.awssdk.core.async.AsyncRequestBody;
+import software.amazon.awssdk.core.exception.SdkClientException;
 import software.amazon.awssdk.testutils.RandomTempFile;
 import software.amazon.awssdk.utils.BinaryUtils;
 
@@ -128,7 +132,8 @@ public void changingFile_fileGetsShorterThanAlreadyRead_failsBecauseTooShort() t
         subscriber.sub.request(Long.MAX_VALUE);
 
         assertThatThrownBy(() -> subscriber.completed.get(5, TimeUnit.SECONDS))
-            .hasCauseInstanceOf(IOException.class);
+            .hasCauseInstanceOf(SdkClientException.class)
+            .hasMessageContaining("File size changed after reading started");
     }
 
     @Test
@@ -154,7 +159,8 @@ public void changingFile_fileGetsShorterThanExistingLength_failsBecauseTooShort(
         subscriber.sub.request(Long.MAX_VALUE);
 
         assertThatThrownBy(() -> subscriber.completed.get(5, TimeUnit.SECONDS))
-            .hasCauseInstanceOf(IOException.class);
+            .hasCauseInstanceOf(SdkClientException.class)
+            .hasMessageContaining("File size changed after reading started");
     }
 
     @Test
@@ -180,7 +186,8 @@ public void changingFile_fileGetsLongerThanExistingLength_failsBecauseTooLong()
         subscriber.sub.request(Long.MAX_VALUE);
 
         assertThatThrownBy(() -> subscriber.completed.get(5, TimeUnit.SECONDS))
-            .hasCauseInstanceOf(IOException.class);
+            .hasCauseInstanceOf(SdkClientException.class)
+            .hasMessageContaining("File size changed after reading started");
     }
 
     @Test
@@ -204,7 +211,61 @@ public void changingFile_fileGetsTouched_failsBecauseUpdatedModificationTime() t
         subscriber.sub.request(Long.MAX_VALUE);
 
         assertThatThrownBy(() -> subscriber.completed.get(5, TimeUnit.SECONDS))
-            .hasCauseInstanceOf(IOException.class);
+            .hasCauseInstanceOf(SdkClientException.class)
+            .hasMessageContaining("File last-modified time changed after reading started");
+    }
+
+    @Test
+    public void preset_modifiedTime_failsBecauseUpdatedModificationTime() throws Exception {
+        FileTime initialModifiedTime = Files.getLastModifiedTime(testFile);
+        // Change the file to be updated
+        Thread.sleep(1_000); // Wait for 1 second so that we are definitely in a different second than when the file was created
+        Files.setLastModifiedTime(testFile, FileTime.from(Instant.now()));
+
+        AsyncRequestBody asyncRequestBody = FileAsyncRequestBody.builder()
+                                                                .path(testFile)
+                                                                .modifiedTimeAtStart(initialModifiedTime)
+                                                                .build();
+        ControllableSubscriber subscriber = new ControllableSubscriber();
+
+        // Start reading file
+        asyncRequestBody.subscribe(subscriber);
+        subscriber.sub.request(Long.MAX_VALUE);
+        assertTrue(subscriber.onNextSemaphore.tryAcquire(5, TimeUnit.SECONDS));
+
+        // Change the file to be updated
+        Thread.sleep(1_000); // Wait for 1 second so that we are definitely in a different second than when the file was created
+        Files.setLastModifiedTime(testFile, FileTime.from(Instant.now()));
+
+
+        // read the second chunk which should now detect the file modification
+        ControllableSubscriber subscriber2 = new ControllableSubscriber();
+        splits.get(1).subscribe(subscriber2);
+        subscriber2.sub.request(Long.MAX_VALUE);
+
+        assertThatThrownBy(() -> subscriber2.completed.get(5, TimeUnit.SECONDS))
+            .hasCauseInstanceOf(SdkClientException.class)
+            .hasMessageContaining("File last-modified time changed after reading started");
     }
 
     @Test
@@ -227,7 +288,8 @@ public void changingFile_fileGetsDeleted_failsBecauseDeleted() throws Exception
         subscriber.sub.request(Long.MAX_VALUE);
 
         assertThatThrownBy(() -> subscriber.completed.get(5, TimeUnit.SECONDS))
-            .hasCauseInstanceOf(IOException.class);
+            .hasCauseInstanceOf(SdkClientException.class)
+            .hasMessageContaining("Unable to check file status after read. Was the file deleted");
     }
 
     @Test
```

I hope this improved pull request resolves the issues and provides a better solution for your requirements.