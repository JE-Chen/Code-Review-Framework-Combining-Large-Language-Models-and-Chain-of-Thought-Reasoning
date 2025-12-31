**PR Summary**

This pull request addresses a bug in the AWS SDK for Java v2's code generation. The bug occurs when generating the code for the endpoint interceptor, where it assumes that the endpoint parameters contain a'region' member. However, endpoint rulesets are not required to have this parameter, and in situations where it doesn't exist, compilation fails.

To fix this issue, the code has been modified to first check if the endpoint parameters have an explicit "region" parameter. If so, it uses that. Otherwise, it falls back to the client region. This change is made for backwards compatibility reasons.

**Changes Made**

The changes are as follows:

1. The code in `EndpointResolverInterceptorSpec.java` has been modified to first check if the endpoint parameters have an explicit "region" parameter. If so, it uses that. Otherwise, it falls back to the client region.
2. Two new tests have been added to `EndpointResolverInterceptorSpecTest.java` to cover the cases where the endpoint parameters have a "region" parameter and where it doesn't.
3. A new file `endpoint-resolve-interceptor-with-multiauthsigv4a-noregionparam.java` has been added to `codegen/src/test/resources` to test