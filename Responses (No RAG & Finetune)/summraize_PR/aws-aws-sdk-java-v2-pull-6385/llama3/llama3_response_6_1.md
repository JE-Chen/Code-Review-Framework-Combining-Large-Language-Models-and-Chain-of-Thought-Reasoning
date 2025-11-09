This GitHub PR addresses a bug in the AWS SDK for Java v2. The bug occurs when generating code for the endpoint interceptor, assuming that the endpoint parameters contain a'region' member. However, endpoint rulesets are not required to have this parameter, leading to compilation failures.

The modifications made in this PR include:

1.  Checking if the endpoint parameters have an explicit'region' parameter. If so, it uses that. Otherwise, it falls back to the client region.

2.  Added new codegen tests to cover the changes.

The changes are made in the `EndpointResolverInterceptorSpec.java` file, specifically in the `modifyRequestMethod` method. The new code checks if the endpoint parameters have an explicit'region' parameter using the `isDeclaredParam` method from `endpointRulesSpecUtils`. If it does, it uses that region; otherwise, it uses the region from the execution attributes.

Additionally, new tests have been added to the `EndpointResolverInterceptorSpecTest.java` file to cover the changes. The tests check that the correct region is used when the endpoint parameters have an explicit'region' parameter and when they do not.

The changes are backward compatible, as they only affect the generation of code for the endpoint interceptor. The existing code will