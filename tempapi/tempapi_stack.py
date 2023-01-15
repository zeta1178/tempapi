from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_ssm,
    aws_s3,
    aws_iam,
    aws_secretsmanager,
    RemovalPolicy,
    Aws,
)

from constructs import Construct

class TempapiStack(Stack):

    @property
    def funct_lambda(self):
        return self.lambda_function

    @property
    def funct_lambda_name(self):
        return self.lambda_name_param.string_value   

    def __init__(self,
        scope: Construct,
        construct_id: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_role = aws_iam.Role(self, "lambda_role",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com")
        )                
        lambda_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))

        # creates lambda function
        self.lambda_function = lambda_.Function(
            self,
            "TempAPI_Lambda",
            code=lambda_.Code.from_asset("lambda"),
            handler="lambda_function.lambda_handler",
            role=lambda_role,
            memory_size=3008,
            timeout=Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_8,
            description="Lambda Function for API Gateway",
        )
 
        # create an SSM parameter for the tempAPI Lambda Name
        self.lambda_name_param = aws_ssm.StringParameter(
            self, "Lambda_Name_Parameter",
            parameter_name="/tempAPI/Lambda_NAME",
            string_value=self.lambda_function.function_name,
            description='tempAPI Lambda Name'
        )
