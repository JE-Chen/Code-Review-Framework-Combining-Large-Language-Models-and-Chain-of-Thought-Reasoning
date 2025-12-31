PR Summary:

Surface errors from FileAsyncRequestBody when files are modified during request.

Key Improvements:

1. Ensure that file modification exceptions in AsyncRequestBody#fromFile are propagated correctly.

Improvement Suggestions:

1. Implement validation of file modification time and size changes during request execution.
2. Update the exception type to SdkClientException for non-retryable exceptions.
3. Capture the initial modification time and file size when the AsyncRequestBody is created.

Meets Requirements:

Yes

Summary: Merge Decision

Do not merge

Reason:

The PR introduces a new feature, and the new feature is not ready for merge.

Additional Notes:

The code introduces a new feature and does not have adequate test coverage or proper documentation.