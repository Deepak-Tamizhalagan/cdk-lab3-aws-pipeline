from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
)
from constructs import Construct

class CdkLab3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function using inline code
        lambda_function = _lambda.Function(
            self,
            "HelloFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",  # Correct handler for inline code
            code=_lambda.Code.from_inline(
                "def handler(event, context):\n"
                "    return {\n"
                "        'statusCode': 200,\n"
                "        'body': 'Hello from Lambda via AWS CodePipeline!'\n"
                "    }"
            ),
        )

        # Create API Gateway REST API
        api_gateway = apigateway.LambdaRestApi(
            self,
            "HelloApiGateway",
            handler=lambda_function,
            proxy=False
        )

        # Add /hello resource
        hello_resource = api_gateway.root.add_resource("hello")
        hello_resource.add_method("GET")

        # Output the API endpoint after deployment
        self.api_url_output = api_gateway.url
