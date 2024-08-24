import pulumi
from dynamo_db import DynamoDBTable

# Example Usage
config = pulumi.Config()
environment = config.require("environment")


# Table 101
DynamoDBTable("myExampleTable", environment=environment, hash_key="id", range_key="sortKey")
