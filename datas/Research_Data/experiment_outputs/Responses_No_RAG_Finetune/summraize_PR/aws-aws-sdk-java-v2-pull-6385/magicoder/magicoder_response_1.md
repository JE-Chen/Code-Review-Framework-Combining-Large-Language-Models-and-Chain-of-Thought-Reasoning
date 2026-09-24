We've updated the endpoint resolver interceptor to use a region from the endpoint parameters if it exists, otherwise fallback to the client region.

In the original code, we assumed that the endpoint parameters contains a'region' member. However, the endpoint rule set does not require this member. 

As a result, in some cases, the compilation fails if the endpoint parameters does not have a'region' member.

This has been updated to use a region from the endpoint parameters if it exists, otherwise fallback to the client region.

This change addresses the issue of the compilation failure when the endpoint parameters does not have a'region' member, and ensures backwards compatibility.