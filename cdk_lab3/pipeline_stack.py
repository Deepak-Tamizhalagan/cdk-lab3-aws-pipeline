from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct
import os

class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, github_repo: str, github_branch: str, codestar_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 🔹 Source Stage - Get code from GitHub using CodeStar connection
        source_output = codepipeline.Artifact()
        source_action = cp_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            owner="Deepak-Tamizhalagan",    # 🔹 your GitHub username
            repo=github_repo,               # eg: "cdk-lab3-aws-pipeline"
            branch=github_branch,           # eg: "main"
            connection_arn=codestar_arn,    # 🔹 To be created in AWS Console
            output=source_output,
        )

        # 🔹 Build Stage - Synth CDK using CodeBuild
        build_project = codebuild.PipelineProject(
            self, "BuildProject",
            environment=dict(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0
            ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "commands": [
                            "npm install -g aws-cdk",
                            "pip install -r requirements.txt"
                        ]
                    },
                    "build": {
                        "commands": [
                            "cdk synth"
                        ]
                    }
                },
                "artifacts": {
                    "files": ["**/*"]
                }
            }),
        )

        build_output = codepipeline.Artifact()
        build_action = cp_actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output,
            outputs=[build_output],
        )

        # 🔹 Deploy Stage - Auto deploy CloudFormation
        deploy_action = cp_actions.CloudFormationCreateUpdateStackAction(
            action_name="Deploy",
            template_path=build_output.at_path("**/*.template.json"),
            stack_name="CdkLab3Stack",
            admin_permissions=True,
        )

        # 🔹 Define Pipeline with Stages
        pipeline = codepipeline.Pipeline(self, "CDKPipeline",
            stages=[
                codepipeline.StageProps(stage_name="Source", actions=[source_action]),
                codepipeline.StageProps(stage_name="Build", actions=[build_action]),
                codepipeline.StageProps(stage_name="Deploy", actions=[deploy_action])
            ]
        )
