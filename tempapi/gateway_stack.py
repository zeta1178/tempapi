from aws_cdk import (
    Aws,
    CfnOutput,
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_apigateway,
)

from constructs import Construct

class GatewayStack(Stack):

    def __init__(self,
        scope: Construct,
        construct_id: str,
        ref_lambda: lambda_.IFunction,
        ref_lambda_name: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
 
        # identifies input lambda
        inputFunction=lambda_.Function.from_function_name(
            self,
            "LambdaFunction",
            function_name=ref_lambda_name,
        )

        # creates api iam policy
        api_resource_policy = iam.PolicyDocument()
        api_resource_policy.add_statements(iam.PolicyStatement(
            actions=["execute-api:Invoke"],
            resources=["execute-api:/*"],                             
            principals=[iam.AnyPrincipal()],
            )
        )

        # creates API Gateway Endpoint
        api_endpoint = aws_apigateway.RestApi(self, "temp_api",
            rest_api_name="Temp API",
            description="Temp API",
            endpoint_types=[aws_apigateway.EndpointType.REGIONAL],
            # policy=api_resource_policy,
        )
 
        # creates lambda integration for input Lambda Function
        api_lambda_integration = aws_apigateway.LambdaIntegration(inputFunction,
            request_templates={"application/json": '{ "statusCode": "200" }'},
        )

        # joins lambda to API gateway endpoint with a method
        api_method="GET"
        api_endpoint.root.add_method(api_method, api_lambda_integration)
 
        # creates new function object from imported Lambda function object
        inputFunction_out = lambda_.Function.from_function_attributes(self, "Function",
            function_arn=inputFunction.function_arn,
            same_environment=True,
            )
       
        #creates resource based policy for API endpoint to invoke lambda function
        inputFunction_out.add_permission(
            "lambdaResourceBasedPolicy",
            action= "lambda:InvokeFunction",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            source_account=f"{Aws.ACCOUNT_ID}",
            source_arn=f"arn:aws:execute-api:{Aws.REGION}:{Aws.ACCOUNT_ID}:{api_endpoint.rest_api_id}/*/{api_method}/"
        )