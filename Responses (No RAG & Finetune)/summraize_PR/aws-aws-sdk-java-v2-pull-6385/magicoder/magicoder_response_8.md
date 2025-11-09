This PR is about resolving an issue in Java SDK v2 where the code generator fails to generate the endpoint resolver interceptor for services that use multiple auth schemes.

When generating the code for the endpoint interceptor, we don't assume that the endpoint params contains a'region' member; endpoint rulesets are not required to have this parameter. If the endpoint params does not have this member, the code generation process fails.

For backwards compatibility, give the region endpoint params preference if it exists; otherwise use the region from the execution attributes.

I've also added tests for this to ensure the proper behavior of the code generation process.