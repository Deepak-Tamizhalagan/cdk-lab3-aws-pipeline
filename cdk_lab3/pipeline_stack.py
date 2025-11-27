from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct


class PipelineStack(Stack):

    def __init__(
        self, scope: Construct, construct_id: str, github_repo: str,
        github_branch: str, codestar_arn: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ###########################
        #  SOURCE: GitHub
        # ###########################
        source_output = codepipeline.Artifact()

        source_action = cp_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            owner="Deepak-Tamizhalagan",  #  GitHub username
            repo=github_repo,             #  "cdk-lab3-aws-pipeline"
            branch=github_branch,         # "main"
            connection_arn=codestar_arn,  # From AWS Console
            output=source_output,
        )

        # ###########################
        # BUILD: Synth CDK
        # ###########################
        build_project = codebuild.PipelineProject(
            self,
            "BuildProject",
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
                            "cdk synth CdkLab3Stack" 
                        ]
                    }
                },
                "artifacts": {
                    "base-directory": "cdk.out",  # Location of synthesized template
                    "files": [
                        "CdkLab3Stack.template.json"  # Exact template to deploy
                    ]
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

        # ###########################
        #  DEPLOY: CloudFormation
        # ###########################

        # Give permissions to create/manage CloudFormation
        deploy_role = iam.Role(
            self,
            "PipelineDeployRole",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
        )

        deploy_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        )

        deploy_action = cp_actions.CloudFormationCreateUpdateStackAction(
            action_name="Deploy",
            stack_name="CdkLab3Stack",
            template_path=build_output.at_path("CdkLab3Stack.template.json"),
            admin_permissions=True,
            deployment_role=deploy_role,
        )

        # ###########################
        # Final Pipeline
        # ###########################
        codepipeline.Pipeline(
            self,
            "CDKPipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[build_action]
                ),
                codepipeline.StageProps(
                    stage_name="Deploy",
                    actions=[deploy_action]
                )
            ],
        )
