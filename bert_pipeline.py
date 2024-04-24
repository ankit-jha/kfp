from datetime import datetime

import google.cloud.aiplatform as aip
from google_cloud_pipeline_components.experimental import custom_job
from google_cloud_pipeline_components.types import artifact_types
from google_cloud_pipeline_components.v1.endpoint import ModelDeployOp
from google_cloud_pipeline_components.v1.model import ModelUploadOp
from kfp.v2 import compiler, dsl
from kfp.v2.components import importer_node

import pipeline_config as cfg
from components.deploy import custom_serving_image, model_archiver
from components.evaluate import metrics
from components.preprocess import preprocess_bert

# Initialize
aip.init(project=cfg.PROJECT_ID, staging_bucket=cfg.BUCKET_URI)

# Create Pipeline
@dsl.pipeline(
    name=cfg.BERT_PIPELINE_NAME,
    description=cfg.BERT_PIPELINE_DESCRIPTION,
    pipeline_root=cfg.PIPELINE_ROOT,
)
def pipeline(
    bucket_name: str = cfg.BERT_TRAINING_DATA_BUCKET,
    blob_name: str = cfg.BERT_TRAINING_DATA,
):

    # Preprocessing Data
    BERT_PROCESSED_DATA = f"{cfg.BUCKET_URI}/{cfg.BERT_PROCESSED_DATA}"
    preprocess_result = preprocess_bert.preprocess(
        bucket_name,
        blob_name,
        BERT_PROCESSED_DATA,
    ).set_display_name("Processing Data")

    # Define Job
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    job_name = f"{cfg.MODEL_NAME}-train-pytorch-py-pkg-{timestamp}"
    gcs_base_output_dir = f"{cfg.PIPELINE_ROOT}/{timestamp}"

    # Training Args
    training_args = [
        "--num-epochs",
        "1",
        "--model-name",
        cfg.MODEL_NAME,
        "--gcs-uri",
        BERT_PROCESSED_DATA,
    ]

    # Python Packaging
    # Python Package needs to be uploaded to the bucket before training.
    # For automation we need a pipeline component to copy the code from git to gcs bucket
    # cd python_package
    # tar cvf bert.tar bert; gzip -f bert.tar; gsutil cp bert.tar.gz gs://${BUCKET_NAME}/bert.tar.gz

    # Define Worker Pool Specs
    worker_pool_specs = [
        {
            "machineSpec": {
                "machineType": cfg.MACHINE_TYPE,
                "acceleratorType": cfg.ACCELERATOR_TYPE,
                "acceleratorCount": cfg.ACCELERATOR_COUNT,
            },
            "replicaCount": cfg.REPLICA_COUNT,
            "pythonPackageSpec": {
                "executorImageUri": cfg.IMAGE_URI,
                "packageUris": [f"{cfg.BUCKET_URI}/bert.tar.gz"],
                "pythonModule": "trainer.task",
                "args": training_args,
            },
        }
    ]

    # Run Model Training
    run_train_task = (
        custom_job.CustomTrainingJobOp(
            project=cfg.PROJECT_ID,
            location=cfg.REGION,
            display_name=job_name,
            base_output_directory=gcs_base_output_dir,
            worker_pool_specs=worker_pool_specs,
        )
        .set_display_name("Run custom training job")
        .after(preprocess_result)
    )

    # Get Training Details And Save Metadata
    training_job_details_task = (
        metrics.get_training_job_details(
            location=cfg.REGION,
            job_resource=run_train_task.output,
            eval_metric_key="eval_accuracy",
            model_display_name=cfg.MODEL_NAME,
        )
        .set_display_name("Get custom training job details")
        .after(run_train_task)
    )

    # Generate Model Archive File (.mar)
    # Model archiver needs certain files to be uploaded to the bucket
    # gsutil cp ./torch/predictor/custom_handler.py gs://${BUCKET_NAME}/${MODEL_NAME}/serve/predictor/
    # gsutil cp ./torch/predictor/index_to_name.json gs://${BUCKET_NAME}/${MODEL_NAME}/serve/predictor/
    # gsutil cp ./torch/predictor/Dockerfile.serve gs://${BUCKET_NAME}/${MODEL_NAME}/serve/

    SERVE_DEPENDENCIES_PATH = f"{cfg.BUCKET_URI}/{cfg.MODEL_NAME}/serve/"
    create_mar_task = (
        model_archiver.generate_mar_file(
            model_display_name=cfg.MODEL_NAME,
            model_version=cfg.VERSION,
            handler=SERVE_DEPENDENCIES_PATH,
            model=training_job_details_task.outputs["model"],
        )
        .set_display_name("Create MAR file")
        .after(training_job_details_task)
    )

    # Build Custom Serving Container Running TorchServe
    build_custom_serving_image_task = (
        custom_serving_image.build_custom_serving_image(
            project=cfg.PROJECT_ID,
            gs_serving_dependencies_path=SERVE_DEPENDENCIES_PATH,
            serving_image_uri=cfg.SERVING_IMAGE_URI,
        )
        .set_display_name("Build custom serving image")
        .after(create_mar_task)
    )

    # Import Model
    import_unmanaged_model_task = (
        importer_node.importer(
            artifact_uri=create_mar_task.outputs["mar_export_uri"],
            artifact_class=artifact_types.UnmanagedContainerModel,
            metadata={
                "containerSpec": {
                    "imageUri": cfg.SERVING_IMAGE_URI,
                    "predictRoute": cfg.SERVING_PREDICT_ROUTE,
                    "healthRoute": cfg.SERVING_HEALTH_ROUTE,
                    "ports": cfg.SERVING_CONTAINER_PORT,
                },
            },
        )
        .set_display_name("Import model")
        .after(build_custom_serving_image_task)
    )

    # Upload Model
    model_upload_op = (
        ModelUploadOp(
            project=cfg.PROJECT_ID,
            display_name=cfg.MODEL_NAME,
            unmanaged_container_model=import_unmanaged_model_task.outputs["artifact"],
        )
        .set_display_name("Upload model")
        .after(import_unmanaged_model_task)
    )

    # Create Endpoint
    from google_cloud_pipeline_components.v1.endpoint import EndpointCreateOp

    endpoint_create_op = (
        EndpointCreateOp(
            project=cfg.PROJECT_ID,
            display_name=f"{cfg.MODEL_NAME}-endpoint",
        )
        .set_display_name("Create endpoint")
        .after(create_mar_task)
    )

    # Deploy Model
    ModelDeployOp(
        endpoint=endpoint_create_op.outputs["endpoint"],
        model=model_upload_op.outputs["model"],
        deployed_model_display_name=cfg.MODEL_NAME,
        dedicated_resources_machine_type=cfg.SERVING_MACHINE_TYPE,
        dedicated_resources_min_replica_count=cfg.SERVING_MIN_REPLICA_COUNT,
        dedicated_resources_max_replica_count=cfg.SERVING_MAX_REPLICA_COUNT,
        traffic_split=cfg.SERVING_TRAFFIC_SPLIT,
    ).set_display_name("Deploy model to endpoint")


# Compile Pipeline Job
compiler.Compiler().compile(pipeline_func=pipeline, package_path=f"{cfg.BERT_PIPELINE_NAME}.json")

# Submit Job
job = aip.PipelineJob(
    display_name=cfg.BERT_PIPELINE_NAME,
    template_path=f"{cfg.BERT_PIPELINE_NAME}.json",
    pipeline_root=cfg.PIPELINE_ROOT,
)

job.run()
