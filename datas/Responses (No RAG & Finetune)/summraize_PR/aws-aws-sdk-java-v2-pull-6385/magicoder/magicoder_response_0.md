As part of our ongoing efforts to improve the AWS SDK for Java V2, we have made an update to the endpoint resolution logic. This PR introduces a new approach to handle endpoint parameters, which is more compatible with the endpoint rulesets used by the AWS SDK for Java V2.

In the code snippet, when the endpoint parameters does not contain a'region' member, we are now checking if the endpoint ruleset has declared a'region' parameter. If not, we fallback to the execution attributes region. This should provide better compatibility with the new endpoint rulesets introduced in AWS SDK for Java V2.

This change also introduces a test case to check if the endpoint resolver interceptor correctly handles the'region' parameter in endpoint rulesets.

As part of the test, we are also ensuring that the region set in the AuthSchemeOption is updated correctly when using the SigV4aAuthScheme.

Please note that this is an internal-only change and might not be directly visible to the end-users. You may also check the generated Java code for the updates.