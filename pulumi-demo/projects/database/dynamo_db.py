import pulumi
import pulumi_aws as aws

class DynamoDBTable:
    def __init__(self, name: str, environment : str, hash_key: str, range_key: str = None):
        self.table = aws.dynamodb.Table(
            name,
            attributes=[
                {
                    "name": hash_key,
                    "type": "S",  # S = String, N = Number, B = Binary
                },
                {
                    "name": range_key,
                    "type": "S",  # Only if range_key is provided
                } if range_key else None,
            ],
            hash_key=hash_key,
            range_key=range_key,
            billing_mode="PAY_PER_REQUEST",  # PAY_PER_REQUEST or PROVISIONED
            tags={
                "Environment": environment,
                "Name": name,
            }
        )
        pulumi.export(f"{name}_table_name", self.table.name)

