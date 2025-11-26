from aws_cdk import App, Environment
from cdk_lab3.cdk_lab3_stack import CdkLab3Stack
from cdk_lab3.pipeline_stack import PipelineStack

app = App()

# Deploy infrastructure stack
infra_stack = CdkLab3Stack(app, "CdkLab3Stack",
    env=Environment(account="886436967620", region="ca-central-1")
)

# Deploy pipeline stack
pipeline_stack = PipelineStack(app, "PipelineStack",
    github_repo="cdk-lab3-aws-pipeline",             
    github_branch="main",                            
    codestar_arn="arn:aws:codeconnections:us-east-2:886436967620:connection/1b96cf67-d0e2-4965-8ff4-937e0be30262",
    env=Environment(account="886436967620", region="ca-central-1")
)

app.synth()
