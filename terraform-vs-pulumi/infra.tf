# main.tf

provider "aws" {
  region = "ap-southeast-2"
}

# Define variables
variable "environment" {
  type    = string
  default = "dev"
}

variable "enable_versioning" {
  type    = bool
  default = true
}

# Generate a unique bucket name using interpolation and functions
resource "aws_s3_bucket" "my_bucket" {
  bucket = "${var.environment}-my-bucket-${random_id.bucket_id.hex}"
  acl    = "private"

  tags = {
    Name        = "MyBucket"
    Environment = var.environment
  }
}

# Create a random ID to append to the bucket name for uniqueness
resource "random_id" "bucket_id" {
  byte_length = 8
}

# Conditionally enable versioning based on a variable
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.my_bucket.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

# Add a lifecycle rule to the bucket
resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  bucket = aws_s3_bucket.my_bucket.id

  rule {
    id     = "log"
    status = "Enabled"

    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      days = 30
    }
  }
}

output "bucket_name" {
  value = aws_s3_bucket.my_bucket.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.my_bucket.arn
}
