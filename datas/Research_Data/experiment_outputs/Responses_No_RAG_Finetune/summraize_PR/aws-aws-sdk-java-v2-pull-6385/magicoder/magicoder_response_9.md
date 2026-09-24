A bug was discovered in the endpoint resolver, interceptor code that would cause the code to fail to compile if the endpoint parameters did not contain a'region' member. 

To resolve this, the code was modified to check if the endpoint parameters did not contain a'region' member before assuming that it had one. Instead, it would fall back to using the region from the execution attributes. 

This change ensures that the code can run in a backwards compatible mode with older SDK versions.