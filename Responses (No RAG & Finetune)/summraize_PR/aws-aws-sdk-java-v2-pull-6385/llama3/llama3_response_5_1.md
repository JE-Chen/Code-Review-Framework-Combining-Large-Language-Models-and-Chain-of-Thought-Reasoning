**Pull Request Summary**

This pull request addresses a bug in the AWS SDK for Java v2 where compilation fails when the endpoint params do not contain a'region' member. The fix is to give the region endpoint params preference if it exists, otherwise use the region from the execution attributes.

**Key Changes**

1. Modified the `EndpointResolverInterceptorSpec` class to check if the endpoint params have an explicit "region" parameter. If so, use that. Otherwise, fallback to the client region.
2. Added new tests to cover the changes, including a new test case for when the endpoint params do not have a "region" parameter.
3. Updated the `DatabaseResolveEndpointInterceptor` class to use the preferred region when creating the `RegionSet` instance.
4. Added a new changelog entry to document the fix.

**Impact**

This change should fix the compilation issue when the endpoint params do not contain a'region' member. It also adds new tests to ensure that the fix works correctly.

**Review Notes**

* The changes look correct and address the issue described.
* The new tests are well-written and cover the different scenarios.
* The changelog entry is clear and concise.
* The code formatting and style are consistent with the rest of the project