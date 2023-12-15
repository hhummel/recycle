import os
from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
)
from constructs import Construct

class RecycleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "RecycleQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        fn = lambda_.Function(self, "GetTrashZoneLowerMerion",
            code=lambda_.Code.from_asset(os.path.join(os.getcwd(), "src")),
            handler="get_trash_zone_lower_merion.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9
        )
