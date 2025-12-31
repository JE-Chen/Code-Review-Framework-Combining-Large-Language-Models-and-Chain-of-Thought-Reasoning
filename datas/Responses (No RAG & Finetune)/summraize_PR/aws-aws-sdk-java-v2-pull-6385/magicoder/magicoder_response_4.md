```
This PR modifies the code generation for endpoint interceptors to not assume that the endpoint params contains a'region' member. For backwards compatibility, it checks if the endpoint params has an explicit "region" parameter. If so, use that. Otherwise, fallback to the client region.

It also adds tests to cover the new functionality.
```