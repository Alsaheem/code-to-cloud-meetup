import os
import sys
from pathlib import Path

rootpath = Path(os.getcwd()).parent.parent
sys.path.append(str(rootpath.joinpath("shared-library")))

import pulumi

from modules.s3.s3_bucket import S3Bucket

config = pulumi.Config()

environment = config.require("environment")

S3Bucket(bucket_name="data-dump", environment=environment , is_public=True, cloudfront_enabled=True )
S3Bucket(bucket_name="habeeb-buck", environment=environment , is_public=False, cloudfront_enabled=False )
S3Bucket(bucket_name="ahmad-buck", environment="production" , is_public=True, cloudfront_enabled=False )
