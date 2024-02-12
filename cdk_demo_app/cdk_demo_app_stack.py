from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3d,
    pipelines as pipelines,
    aws_lambda as _lambda,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions
)
from constructs import Construct

class CdkDemoAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # Define S3 buckets
        source_bucket = s3.Bucket(self, "SourceBucket")
        output_bucket = s3.Bucket(self, "OutputBucket")

        # Deploy source file (replace with your file)
        s3d.BucketDeployment(self, "SourceFileDeployment",
                        destination_bucket=source_bucket,
                        sources=[s3d.Source.asset("/Users/bmh/git/cdk-demo-app/samples/")])

        # CodeBuild project to transform the file
        build_project = codebuild.PipelineProject(self, "BuildProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "commands": ["pip install -r requirements.txt"]
                    },
                    "build": {
                        "commands": ["python transform_file.py"]
                    }
                },
                "artifacts": {
                    "files": ["output/**"]
                }
            })
        )

        # Lambda function to handle deployment
        transform_lambda = _lambda.Function(self, "TransformLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda_code"),
            handler="index.handler"
        )

                # Define pipeline stages
        source_output = codepipeline.Artifact("SourceArtifact")
        source_action = codepipeline_actions.S3SourceAction(
            action_name="S3Source",
            bucket=source_bucket,
            bucket_key="landing",
            output=source_output
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=build_project,
            input=source_output,
        )

        deploy_action = codepipeline_actions.S3DeployAction(
            action_name="S3Deploy",
            input=source_output,
            bucket=output_bucket
        )

        # Create the pipeline
        pipeline = codepipeline.Pipeline(self, "MyPipeline",
            pipeline_name="FileProcessingPipeline"
        )
        pipeline.add_stage(stage_name="Source", actions=[source_action])
        pipeline.add_stage(stage_name="Build", actions=[build_action])
        pipeline.add_stage(stage_name="Deploy", actions=[deploy_action])



