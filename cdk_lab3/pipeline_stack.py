from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as codebuild,
)
from constructs import Construct


class PipelineStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        github_repo: str,
        github_branch: str,
        codestar_arn: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ==========================
        # 1. Source Stage (GitHub)
        # ==========================
        source_output = codepipeline.Artifact()

        source_action = cp_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            owner="Deepak-Tamizhalagan",     # 👈 Your GitHub username
            repo=github_repo,               # e.g., "cdk-lab3-aws-pipeline"
            branch=github_branch,           # e.g., "main"
            connection_arn=codestar_arn,    # 👈 The ARN you created
            output=source_output,
        )

        # ==========================
        #  2. Build Stage (CDK Synth)
        # ==========================
        build_project = codebuild.PipelineProject(
            self,
            "BuildProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                privileged=True  # 👈 Required for CDK/Docker access
            ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "commands": [
                            "npm install -g aws-cdk",  # Install CDK
                            "pip install -r requirements.txt"
                        ]
                    },
                    "build": {
                        "commands": [
                            "cdk synth CdkLab3Stack"  # 👈 Synth ONLY your app stack
                        ]
                    }
                },
                "artifacts": {
                    "base-directory": "cdk.out",  # 👈 Source of templates
                    "files": [
                        "CdkLab3Stack.template.json"  # 👈 Deploy this file
                    ]
                }
            })
        )

        build_output = codepipeline.Artifact()

        build_action = cp_actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output,
            outputs=[build_output],
        )

        # ==========================
        #  3. Deploy Stage
        # ==========================
        deploy_action = cp_actions.CloudFormationCreateUpdateStackAction(
            action_name="Deploy",
            stack_name="CdkLab3Stack",
            template_path=build_output.at_path("CdkLab3Stack.template.json"),
            admin_permissions=True,
        )

        # ==========================
        #  4. Final Pipeline Setup
        # ==========================
        pipeline = codepipeline.Pipeline(
            self,
            "CDKPipeline",
            stages=[
                codepipeline.StageProps(stage_name="Source", actions=[source_action]),
                codepipeline.StageProps(stage_name="Build", actions=[build_action]),
                codepipeline.StageProps(stage_name="Deploy", actions=[deploy_action]),
            ]
        )
