import pulumi
import pulumi_aws as aws
from users_and_groups import users, groups

class UserGroupIamMgt:
    def __init__(self):
        self.create_groups()
        self.create_users()
        self.iam_user_group_memberships()

    def create_groups(self):
        for group in groups:
            self.group = aws.iam.Group(f"{group['group_name']}_group",  name=group["group_name"], path=group["path"])

    def create_users(self):
        for user in users:
            self.group = aws.iam.User(f"{user['email']}_user" , name= user["email"])

    def iam_user_group_memberships(self):
        for iam_user in users:
            aws.iam.UserGroupMembership(f"{iam_user['email']}_membership",
                user=iam_user["email"],
                groups=[iam_user["group"]],
            )

    # Export the IAM user names
    pulumi.export("iam_user_names", [user["email"] for user in users])
