# PR Review: Surface errors from FileAsyncRequestBody when files are modified during request

## Conclusion
**Recommend Merge**

The PR addresses a critical issue with file modification error handling in the SDK's asynchronous file request handling. The changes are well-structured, thoroughly tested, and fix a real problem that could lead to silent failures in file uploads.

## Key Strengths
- Correctly identifies and fixes the root cause (validation happening too late after Netty cancels the subscription)
- Changes the exception type from retryable IOException to non-retryable SdkClientException (proper semantic)
- Ensures consistent file state capture across retries/splits (critical for multi-part uploads)
- Adds comprehensive tests covering all scenarios (file size change, modification time change, split uploads)
- Maintains backward compatibility with existing API
- Provides helpful error messages with detailed timestamps

## Improvement Suggestions
1. **Fix duplicate changelog entries** - The PR contains two identical changelog files (`.changes/next-release/bugfix-AWSSDKforJavav2-4bab915.json`). Only one should exist. This is a minor but important fix before merging.

2. **Improve error message for file size change** - The current message "File size changed after reading started. Initial size: 10. Current size: 20." could be enhanced to include the expected size. For example: "File size changed after reading started. Expected size: 10, Initial size: 10, Current size: 20."

3. **Test case naming improvement** - The test `preset_modifiedTime_failsBecauseUpdatedModificationTime` could be more descriptive. Consider renaming to `fileAsyncRequestBody_with_preset_modified_time_detects_file_modification`.

4. **Consider adding a test for null modifiedTimeAtStart** - While the code handles null values, adding a test case explicitly verifying behavior when `modifiedTimeAtStart` is null would provide additional confidence.

## Why This Merits Approval

The PR solves a genuine problem where file modifications during upload would silently fail (due to the error never being propagated), which could lead to data corruption without any indication to the user. The fix is:
- Well-justified with clear explanation of the issue
- Implemented cleanly without adding significant complexity
- Thoroughly tested across all relevant scenarios
- Maintains API compatibility
- Correctly changes the exception type to reflect the non-retryable nature of the error

The only issue is the duplicate changelog entry, which is a simple fix that should be addressed before merging.

## Final Assessment

This is a high-quality PR that fixes a critical bug in the SDK's file handling. The solution is elegant and well-executed. The minor issue with the duplicate changelog is easily fixable and shouldn't prevent merging. The PR meets all quality criteria for merging into the main branch.