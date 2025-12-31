This GitHub PR is a bug fix for the AWS SDK for Java v2. The bug fix addresses an issue where the code generation for the endpoint interceptor would fail when the endpoint params did not contain a'region' member.

Here's a summary of the changes:

* The code generator is modified to no longer assume that the endpoint params contains a'region' member. Instead, it checks if the endpoint ruleset has a'region' parameter. If it does, it uses that; otherwise, it falls back to the client region.
* The test suite has been updated to include new tests for the modified code generator. These tests cover both cases where the endpoint params contains a'region' member and where it does not.
* A new changelog entry has been added to document the bug fix.

The changes are located in the following files:

* `codegen/src/main/java/software/amazon/awssdk/codegen/poet/rules/EndpointResolverInterceptorSpec.java`: This is where the code generator is modified to check for the presence of a'region' parameter in the endpoint ruleset.
* `codegen/src/test/java/software/amazon/awssdk/codegen/poet/rules/EndpointResolverInterceptorSpecTest.java`: This is where the new tests are added