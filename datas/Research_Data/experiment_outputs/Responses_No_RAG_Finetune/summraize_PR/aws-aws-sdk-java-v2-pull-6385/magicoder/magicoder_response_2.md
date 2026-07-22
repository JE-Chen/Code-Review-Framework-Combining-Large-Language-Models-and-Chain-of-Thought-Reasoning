This PR focuses on implementing a new feature for AWS SDK for Java v2. This PR adds support for the SigV4a authentication scheme for Amazon RDS, which enables the client to make requests to the Amazon RDS service using SigV4a. This new feature provides improved security and compliance requirements.

The `EndpointResolverInterceptorSpec` class is modified to accommodate this new scheme and also to ensure backward compatibility when the AWS Region is not explicitly provided in the endpoint parameters. If the `region` parameter is not found in the endpoint parameters, the PR retrieves the AWS Region from the execution attributes, maintaining the previous behavior.

The `EndpointResolverInterceptorSpecTest` class also gets updated to include new test cases for the newly added feature.

The `endpoint-resolve-interceptor-with-multiauthsigv4a-noregionparam.java` file is added to generate the modified class within the test resources.

This PR also includes the necessary changes in the Javadoc documentation, changelog, and `.changes` folder.

This PR can be released under the Apache 2