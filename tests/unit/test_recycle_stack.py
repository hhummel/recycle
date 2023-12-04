import aws_cdk as core
import aws_cdk.assertions as assertions

from recycle.recycle_stack import RecycleStack

# example tests. To run these tests, uncomment this file along with the example
# resource in recycle/recycle_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RecycleStack(app, "recycle")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
