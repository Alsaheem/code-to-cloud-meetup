import pulumi
from pulumi import Config, export
import pulumi_aws as aws
import pulumi_random as random

# Define a Pulumi configuration to use for environment and versioning
config = Config()
environment = config.get("environment") or "dev"
enable_versioning = config.get_bool("enableVersioning") or True

# Create a random ID for bucket name uniqueness
bucket_id = random.RandomId("bucketId",
    byte_length=8,
)

# Create an S3 bucket with a dynamically generated name
bucket = aws.s3.Bucket("myBucket",
    bucket=f"{environment}-my-bucket-{bucket_id.hex}",
    acl="private",
    tags={
        "Name": "MyBucket",
        "Environment": environment,
    }
)

# Conditionally enable versioning based on a configuration setting
if enable_versioning:
    versioning = aws.s3.BucketVersioning("versioning",
        bucket=bucket.id,
        versioning_configuration={
            "status": "Enabled",
        }
    )

# Add a lifecycle rule to the bucket
lifecycle = aws.s3.BucketLifecycleConfiguration("lifecycle",
    bucket=bucket.id,
    rules=[{
        "id": "log",
        "status": "Enabled",
        "expiration": {
            "days": 90,
        },
        "noncurrent_version_expiration": {
            "days": 30,
        },
    }],
)

# Export the bucket name and ARN
export("bucket_name", bucket.bucket)
export("bucket_arn", bucket.arn)
