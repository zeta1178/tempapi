from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_ssm,
    aws_s3,
    aws_ec2 as ec2,
    aws_iam,
    aws_secretsmanager,
    RemovalPolicy,
    Aws,
    CfnOutput,
)
from aws_cdk.aws_ec2 import Vpc, NatProvider, SubnetConfiguration, SubnetType
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

        # network components VPC subnets
        # Subnet configurations for a private tier and public
        subnet1 = SubnetConfiguration(
                name="PublicSubnet",
                subnet_type=SubnetType.PUBLIC,
                cidr_mask=28)
        subnet2 = SubnetConfiguration(
                name="PrivateSubnet",
                subnet_type=SubnetType.PRIVATE_WITH_EGRESS,
                cidr_mask=28)

        vpc = ec2.Vpc(self, "tempapiVPC",
            # cidr                 = "10.0.0.0/27",
            ip_addresses= ec2.IpAddresses.cidr("10.0.0.0/27"),
            nat_gateways         = 1,
            max_azs              = 1,
            subnet_configuration = [subnet1, subnet2]
            )

        vpc_subnets_pub = vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC)
        vpc_subnets_priv = vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)

        subnet_ids_pub = []
        for subnet in vpc_subnets_pub.subnets:
          subnet_ids_pub.append(subnet.subnet_id)
        subnet_ids_pub_str= (','.join(subnet_ids_pub))
        subnet_ids_priv = []
        
        for subnet in vpc_subnets_priv.subnets:
          subnet_ids_priv.append(subnet.subnet_id)
        subnet_ids_priv_str= (','.join(subnet_ids_priv))
        vpc_id = vpc.vpc_id

        CfnOutput(
            self, "VPC ID",
            description="VPC ID",
            value=vpc_id
        )

        CfnOutput(
            self, "Subnet IDs Pub",
            description="Subnet IDs",
            value=subnet_ids_pub_str
        )

        CfnOutput(
            self, "Subnet IDs Priv",
            description="Subnet IDs",
            value=subnet_ids_priv_str
        )

        # create an SSM parameter vpc id
        vpc_param = aws_ssm.StringParameter(
            self, "VPC_Parameter",
            parameter_name="/gwapi/vpc",
            string_value=vpc_id,
            description='vpc id'
        )

        # create an SSM parameter subnet public
        subnet_public_param = aws_ssm.StringParameter(
            self, "Subnet_Public_Parameter",
            parameter_name="/gwapi/subnet_public",
            string_value=subnet_ids_pub_str,
            description='subnet public'
        )

        # create an SSM parameter subnet private
        subnet_private_param = aws_ssm.StringParameter(
            self, "Subnet_Private_Parameter",
            parameter_name="/etl/subnet_private",
            string_value=subnet_ids_priv_str,
            description='subnet private'
        )

        # creates IAM role for lambda function 
        lambda_role = aws_iam.Role(self, "lambda_role",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com")
        )                
        # assing managed policy to the lambda role
        lambda_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))

        # creates lambda function
        self.lambda_function = lambda_.Function(
            self,
            "TempAPI_Lambda",
            code=lambda_.Code.from_asset("lambda"),
            handler="lambda_function.lambda_handler",
            role=lambda_role,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            memory_size=3008,
            timeout=Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_8,
            description="Lambda Function for API Gateway",
        )
 
        # create an SSM parameter for the tempAPI Lambda Name
        self.lambda_name_param = aws_ssm.StringParameter(
            self, "Lambda_Name_Parameter",
            parameter_name="/gwapi/Lambda_NAME",
            string_value=self.lambda_function.function_name,
            description='GAteway API Lambda Name'
        )
