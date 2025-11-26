import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_lab3.cdk_lab3_stack import CdkLab3Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_lab3/cdk_lab3_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkLab3Stack(app, "cdk-lab3")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
