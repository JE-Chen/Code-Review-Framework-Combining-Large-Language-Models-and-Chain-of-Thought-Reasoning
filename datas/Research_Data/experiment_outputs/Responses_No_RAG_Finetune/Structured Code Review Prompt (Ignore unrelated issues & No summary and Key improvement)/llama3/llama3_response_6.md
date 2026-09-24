[Improvement Suggestions]  
- Refactor the `validateFileUnchangedAndSignalErrors` method in `FileAsyncRequestBody` to reduce its Cognitive Complexity from 21 to the 15 allowed.
- Remove the `public` modifier from the `signalOnError` method in `FileAsyncRequestBody`.
- Replace the use of `Thread.sleep()` in the `preset_modifiedTime_failsBecauseUpdatedModificationTime` and `split_changingFile_fileGetsTopped_failsBecauseUpdatedModificationTime` tests in `FileAsyncRequestBodyTest` with a more reliable way to wait for the file modification time to change.

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The code changes address the three issues listed in the PR message and meet the requirements. The refactoring of the `validateFileUnchangedAndSignalErrors` method and the removal of the `public` modifier from the `signalOnError` method are necessary improvements. The use of `Thread.sleep()` in the tests can be replaced with a more reliable way to wait for the file modification time to change.

[Additional Notes]  
None.