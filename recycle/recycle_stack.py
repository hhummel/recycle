import os
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_dynamodb as dynamodb
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

        lm_zone_function = lambda_.Function(
            self, 
            "GetTrashZoneLowerMerion",
            code=lambda_.Code.from_asset(os.path.join(os.getcwd(), "src")),
            handler="get_trash_zone_lower_merion.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9
        )

        state_machine = sfn.StateMachine(
            self, 
            "ConfigureUserStateMachine",
            definition=tasks.LambdaInvoke(
                self, "ZoneTask",
                lambda_function=lm_zone_function
            ).next(sfn.Succeed(self, "GreetedWorld"))
        )
