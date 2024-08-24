import pulumi
from static_website import StaticWebsite

config = pulumi.Config()
s3_bukets = config.require_object("s3Bukets")
static_website = []
for range in [{"key": k, "value": v} for [k, v] in enumerate({key: val for key, val in s3_bukets if val.created_status == True})]:
    static_website.append(StaticWebsite(f"static-website-{range['key']}", {
'bucketName': range["value"]["bucketName"]    }))
