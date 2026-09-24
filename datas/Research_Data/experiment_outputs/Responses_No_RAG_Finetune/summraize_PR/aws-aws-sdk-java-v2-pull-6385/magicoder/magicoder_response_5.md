The summary of this PR is that the code generation is improved to handle the situation where the endpoint params does not contain a "region" member. In those situations, the code used to fail to compile. 

The solution is to give preference to the "region" member in the endpoint params. Otherwise, use the region from the execution attributes.

This PR introduces a new method `ruleParams`, which is used to construct the `DatabaseEndpointParams`. The method uses two `try-catch` blocks, one for the custom logic and the other for the endpoint resolution failure. 

The 'AwsEndpointProviderUtils' class has been introduced to encapsulate the logic of handling the execution attributes. It provides methods to get the region and endpoint from the execution attributes. 

The `endpointIsDiscovered`, `disableHostPrefixInjection`, `endpointBuiltIn` and `regionBuiltIn` methods are introduced to separate the logic of checking whether an endpoint is discovered, whether host prefix is disabled, getting the endpoint and region from built-in attributes, respectively. 

The method `authSchemeWithEndpointSignerProperties