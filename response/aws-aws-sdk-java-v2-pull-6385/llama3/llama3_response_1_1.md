**PR Summary**

This pull request addresses a bug in the AWS SDK for Java v2. The bug occurs when generating code for the endpoint interceptor, where it assumes that the endpoint params contain a'region' member. However, endpoint rulesets are not required to have this parameter, which leads to compilation failures.

The PR modifies the code to give the region endpoint params preference if it exists, and otherwise use the region from the execution attributes. This ensures backwards compatibility and prevents compilation failures.

**Changes**

* Modified the `EndpointResolverInterceptorSpec` class to check if the endpoint params have an explicit "region" parameter before using it to create a `RegionSet`.
* If the "region" parameter is not present, it falls back to using the region from the execution attributes.
* Added new tests to cover the scenarios where the endpoint params have and do not have a "region" parameter.

**Impact**

This PR fixes a bug that could cause compilation failures when generating code for the endpoint interceptor. It also ensures backwards compatibility by giving preference to the region endpoint params if they exist.

**Testing**

The PR includes new tests to cover the scenarios where the endpoint params have and do not have a "region" parameter. These tests ensure that the code behaves correctly in both cases