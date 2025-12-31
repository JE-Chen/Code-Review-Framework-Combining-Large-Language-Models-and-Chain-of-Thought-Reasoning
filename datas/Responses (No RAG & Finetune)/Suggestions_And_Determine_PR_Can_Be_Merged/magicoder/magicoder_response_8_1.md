Do Not Merge

The PR contains several issues:

1. The logic for validating the file modification time is incorrect. The PR code doesn't properly check the file modification time before calling `onNext`, which could lead to the error being signaled prematurely.

2. The exceptions are raised as IOExceptions, which is incorrect. The exceptions should be raised as SdkClientExceptions, since they are terminal and should not be retried.

3. The `modifiedTimeAtStart` and `sizeAtStart` are not correctly captured when the PR is created. This could lead to the wrong file status being checked, causing incorrect behavior.

4. The code has a high Cognitive Complexity (21). It is recommended to refactor the code to reduce the complexity.

5. The test cases are failing, due to incorrect behavior or incorrect test cases. The test cases should be updated or fixed to pass.

6. The tests are not passing. The tests should be updated or fixed to pass.

7. The code style is not consistent. It is recommended to follow the code style guide of the project.

8. The PR doesn't include the necessary documentation or the necessary Javadoc comments. It is recommended to include the necessary documentation or Javadoc comments.

9. The PR does not have the necessary checks or the necessary tests. It is recommended to add the necessary checks or tests.

10. The PR does not follow the guidelines for contributing to the project. It is recommended to follow the guidelines for contributing to the project.

11. The PR does not have a changelog entry. It is recommended to add a changelog entry.

12. The PR does not have a license. It is recommended to add a license.

The PR should be reviewed and potentially reworked before it can be merged.