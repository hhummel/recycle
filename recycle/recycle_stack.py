import os
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_dynamodb as dynamodb,
    aws_cognito as cognito,
    aws_apigateway as gateway,
)
from constructs import Construct


class RecycleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        dynamodb.Table(self, "RecycleUserTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            table_name="RecycleUserTable",
            deletion_protection=True,
        )

        pool = cognito.UserPool(self, "Pool")
        pool.add_client(
            "app-client",
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True
                ),
                scopes=[cognito.OAuthScope.OPENID],
                callback_urls=["https://sashette.com/welcome"],
                logout_urls=["https://sashette.com/signin"]
            )
        )

        api = gateway.RestApi(self, "recycle-api")
        api.root.add_method("ANY")
        users = api.root.add_resource("users")
        users.add_method("GET")
        users.add_method("POST")
        user = users.add_resource("{user_id}")
        user.add_method("GET")
        user.add_method("DELETE")
        user.add_method("PATCH")

        lm_zone_function = lambda_.Function(
            self, 
            "GetTrashZoneLowerMerion",
            code=lambda_.Code.from_asset(os.path.join(os.getcwd(), "src")),
            handler="get_trash_zone_lower_merion.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9
        )
