import pulumi
from pulumi_aws import s3, cloudfront
from helpers.constants import COMPANY_NAME
from helpers.utils import is_valid_bucket_name

# Create an S3 bucket
class S3Bucket:
    def __init__(self, bucket_name :str , environment : str, is_public : bool , cloudfront_enabled : bool):
        self.bucket_name = bucket_name
        self.is_public = is_public
        self.environment = environment
        self.cloudfront_enabled = cloudfront_enabled
        self._create_bucket()

    def _create_bucket(self):

        new_bucket_name = f"{self.bucket_name}.{self.environment}.{COMPANY_NAME}.com"
        is_bucket_name_valid = is_valid_bucket_name(bucket_name=self.bucket_name)

        if is_bucket_name_valid is False:
            pulumi.error("The bucket name is invalid , please check for misconfigurations")
            raise Exception(f"Bucket name {new_bucket_name} is invalid")

        
        if self.environment.lower() == "production" and self.is_public is True:
            raise Exception("Public access not allowed for prod environments")
        
        self.s3_bucket = s3.BucketV2(f'{self.bucket_name}_Bucket', bucket=new_bucket_name)
        
        if self.is_public is True:

            s3.BucketPublicAccessBlock(f"{self.bucket_name}_bucketPublicAccessBlockResource",
                bucket=self.s3_bucket.id,
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            )

            # Define a bucket policy to make the bucket public
            s3.BucketPolicy(f'{self.bucket_name}_bucketPolicy',
                bucket=self.s3_bucket.id,
                policy=self.s3_bucket.id.apply(lambda bucket_id: f"""{{
                    "Version": "2012-10-17",
                    "Statement": [
                        {{
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": "arn:aws:s3:::{bucket_id}/*"
                        }}
                    ]
                }}""")
            )

        if self.cloudfront_enabled is True:

            # Create an origin access identity for CloudFront
            origin_access_identity = cloudfront.OriginAccessIdentity(f"{self.bucket_name}_originAccessIdentity")

            # Grant the Origin Access Identity access to the S3 bucket
            bucket_access_policy = s3.BucketPolicy(f"{self.bucket_name}_bucketAccessPolicy",
                bucket=self.s3_bucket.id,
                policy=pulumi.Output.all(self.s3_bucket.id, origin_access_identity.iam_arn).apply(lambda args: f"""{{
                    "Version": "2012-10-17",
                    "Statement": [
                        {{
                            "Effect": "Allow",
                            "Principal": {{
                                "AWS": "{args[1]}"
                            }},
                            "Action": "s3:GetObject",
                            "Resource": "arn:aws:s3:::{args[0]}/*"
                        }}
                    ]
                }}""")
            )

            # Create a CloudFront distribution
            distribution = cloudfront.Distribution(f"{self.bucket_name}_myCDN",
                origins=[cloudfront.DistributionOriginArgs(
                    domain_name=self.s3_bucket.bucket_regional_domain_name,
                    origin_id=self.s3_bucket.arn,
                    s3_origin_config=cloudfront.DistributionOriginS3OriginConfigArgs(
                        origin_access_identity=origin_access_identity.cloudfront_access_identity_path,
                    )
                )],
                enabled=True,
                is_ipv6_enabled=True,
                default_root_object="index.html",
                default_cache_behavior=cloudfront.DistributionDefaultCacheBehaviorArgs(
                    allowed_methods=["GET", "HEAD", "OPTIONS"],
                    cached_methods=["GET", "HEAD"],
                    target_origin_id=self.s3_bucket.arn,
                    forwarded_values=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
                        query_string=False,
                        cookies=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                            forward="none"
                        )
                    ),
                    viewer_protocol_policy="redirect-to-https",
                    min_ttl=0,
                    default_ttl=3600,
                    max_ttl=86400,
                ),
                price_class="PriceClass_100",
                restrictions=cloudfront.DistributionRestrictionsArgs(
                    geo_restriction=cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                        restriction_type="none"
                    )
                ),
                viewer_certificate=cloudfront.DistributionViewerCertificateArgs(
                    cloudfront_default_certificate=True,
                )
            )



        # Export the bucket name
        pulumi.export('bucket_name', self.s3_bucket.id)

    