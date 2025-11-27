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
        # 1) SOURCE STAGE – GitHub
        # ==========================
        source_output = codepipeline.Artifact()

        source_action = cp_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            owner="Deepak-Tamizhalagan",     # GitHub username
            repo=github_repo,               # e.g. "cdk-lab3-aws-pipeline"
            branch=github_branch,           # e.g. "main"
            connection_arn=codestar_arn,    # CodeStar connection ARN
            output=source_output,
        )

        # ==========================
        # 2) BUILD STAGE – synth CDK
        # ==========================
        build_project = codebuild.PipelineProject(
            self,
            "BuildProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
            ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "commands": [
                            "npm install -g aws-cdk",
                            "pip install -r requirements.txt",
                        ]
                    },
                    "build": {
                        "commands": [
                            # create custom output folder
                            "mkdir -p output",
                            # synth only the app stack into ONE file
                            "cdk synth CdkLab3Stack > output/CdkLab3Stack.template.json",
                            # debug: show files so we can see them in logs
                            "echo '--- FILES AFTER SYNTH ---'",
                            "ls -R",
                        ]
                    },
                },
                "artifacts": {
                    # include exactly this path in build artifact
                    "files": [
                        "output/CdkLab3Stack.template.json",
                    ],
                },
            }),
        )

        build_output = codepipeline.Artifact()

        build_action = cp_actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output,
            outputs=[build_output],
        )

        # ==========================
        # 3) DEPLOY STAGE – CFN
        # ==========================
        deploy_action = cp_actions.CloudFormationCreateUpdateStackAction(
            action_name="Deploy",
            stack_name="CdkLab3Stack",
            # must match path inside artifact exactly
            template_path=build_output.at_path("output/CdkLab3Stack.template.json"),
            admin_permissions=True,
        )

        # ==========================
        # 4) PIPELINE DEFINITION
        # ==========================
        codepipeline.Pipeline(
            self,
            "CDKPipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action],
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[build_action],
                ),
                codepipeline.StageProps(
                    stage_name="Deploy",
                    actions=[deploy_action],
                ),
            ],
        )
