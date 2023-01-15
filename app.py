#!/usr/bin/env python3
import os
import yaml

import aws_cdk as cdk
from aws_cdk import App, Tags, Environment

from tempapi.tempapi_stack import TempapiStack
from tempapi.gateway_stack import GatewayStack

# loads local config
config=yaml.safe_load(open('config.yml'))

local_env=Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=config['env']['region']
)

app = cdk.App()
tempapi=TempapiStack(app, 
    "TempapiStack",
    env=local_env,
    )
gateway=GatewayStack(app, 
    "GatewayStack",
    ref_lambda=tempapi.funct_lambda,
    ref_lambda_name=tempapi.funct_lambda_name,
    env=local_env,
    )
app.synth()
