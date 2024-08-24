import pulumi
from pulumi import Input
from typing import Optional, Dict, TypedDict, Any
import json
import pulumi_aws as aws

class StaticWebsiteArgs(TypedDict, total=False):
    bucketName: Input[str]

class StaticWebsite(pulumi.ComponentResource):
    def __init__(self, name: str, args: StaticWebsiteArgs, opts:Optional[pulumi.ResourceOptions] = None):
        super().__init__("components:index:StaticWebsite", name, args, opts)

        # Creating an s3 bucket
        s3_bucket = aws.s3.BucketV2(f"{name}-s3_bucket",
            bucket=args["bucketName"],
            tags={
                "Environment": "production",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # Creating s3 bucket ownership control
        s3_bucket_ownership_control = aws.s3.BucketOwnershipControls(f"{name}-s3_bucket_ownership_control",
            bucket=s3_bucket.id,
            rule={
                "object_ownership": "ObjectWriter",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # Creating public access control
        s3_bucket_access_control = aws.s3.BucketPublicAccessBlock(f"{name}-s3_bucket_access_control",
            bucket=s3_bucket.id,
            block_public_acls=False,
            block_public_policy=False,
            ignore_public_acls=False,
            restrict_public_buckets=False,
            opts = pulumi.ResourceOptions(parent=self))

        # Creating access control list
        s3_bucket_access_control_list = aws.s3.BucketAclV2(f"{name}-s3_bucket_access_control_list",
            bucket=s3_bucket.id,
            acl="public-read",
            opts = pulumi.ResourceOptions(parent=self,
                depends_on=[
                    s3_bucket_ownership_control,
                    s3_bucket_access_control,
                ]))

        # Creating website configuration
        static_website = aws.s3.BucketWebsiteConfigurationV2(f"{name}-static_website",
            bucket=s3_bucket.id,
            index_document={
                "suffix": "index.html",
            },
            error_document={
                "key": "index.html",
            },
            opts = pulumi.ResourceOptions(parent=self))

        # Creating bucket policy
        bucket_policy = aws.s3.BucketPolicy(f"{name}-bucket_policy",
            bucket=s3_bucket.id,
            policy=pulumi.Output.json_dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                    ],
                    "Resource": [
                        s3_bucket.arn.apply(lambda arn: f"{arn}/*"),
                        s3_bucket.arn,
                    ],
                }],
            }),
            opts = pulumi.ResourceOptions(parent=self))

        s3_origin_id = "myS3Origin"

        oai = aws.cloudfront.OriginAccessIdentity(f"{name}-oai", comment=f"OAI for {args["bucketName"]}",
        opts = pulumi.ResourceOptions(parent=self))

        # Creating cloudfront distribution
        s3_distribution = aws.cloudfront.Distribution(f"{name}-s3_distribution",
            origins=[{
                "domain_name": s3_bucket.bucket_regional_domain_name,
                "origin_id": s3_origin_id,
                "s3_origin_config": {
                    "origin_access_identity": oai.cloudfront_access_identity_path,
                },
            }],
            enabled=True,
            is_ipv6_enabled=True,
            default_cache_behavior={
                "allowed_methods": [
                    "DELETE",
                    "GET",
                    "HEAD",
                    "OPTIONS",
                    "PATCH",
                    "POST",
                    "PUT",
                ],
                "cached_methods": [
                    "GET",
                    "HEAD",
                ],
                "target_origin_id": s3_origin_id,
                "forwarded_values": {
                    "query_string": False,
                    "cookies": {
                        "forward": "none",
                    },
                },
                "viewer_protocol_policy": "allow-all",
                "min_ttl": 0,
                "default_ttl": 3600,
                "max_ttl": 86400,
            },
            restrictions={
                "geo_restriction": {
                    "restriction_type": "none",
                },
            },
            custom_error_responses=[
                {
                    "error_caching_min_ttl": 10,
                    "error_code": 403,
                    "response_code": 200,
                    "response_page_path": "/index.html",
                },
                {
                    "error_caching_min_ttl": 10,
                    "error_code": 404,
                    "response_code": 200,
                    "response_page_path": "/index.html",
                },
            ],
            tags={
                "Environment": "production",
            },
            viewer_certificate={
                "cloudfront_default_certificate": True,
            },
            opts = pulumi.ResourceOptions(parent=self))

        self.register_outputs()
