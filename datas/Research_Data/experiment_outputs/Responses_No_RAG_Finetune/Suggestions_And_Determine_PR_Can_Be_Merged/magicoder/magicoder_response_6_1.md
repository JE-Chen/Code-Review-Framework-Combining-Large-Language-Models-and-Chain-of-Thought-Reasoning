PR messages:

Recommend Merge

Improvement Suggestions:

- ...
- ...

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
+        } else