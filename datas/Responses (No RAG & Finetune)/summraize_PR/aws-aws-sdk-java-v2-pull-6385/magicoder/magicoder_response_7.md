This PR introduces a new feature where the endpoint resolver interceptor will prefer the region from the endpoint params if it exists. If the endpoint params does not contain a region member, the interceptor will fallback to the client region. This is to maintain backwards compatibility with old SDKs that may not have a region member in endpoint params.

The change introduces a new class `DatabaseResolveEndpointInterceptor` which extends the `ExecutionInterceptor` from `AWS SDK for Java`. This class is responsible for modifying the SDK request and http request and also setting the metric values and endpoint parameters.

The change introduces a new method `ruleParams` which sets the endpoint parameters. This method is used to build the `DatabaseEndpointParams` object which is used to resolve the endpoint.

The method `authSchemeWithEndpointSignerProperties` is used to match the endpoint auth scheme with the SDK auth scheme. If the auth scheme is SigV4 or SigV4a, it sets the properties like `disableDoubleEncoding`, `signingRegion`, `signingName`, `signingRegionSet` and `serviceSign