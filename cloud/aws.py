import os
import re
from collections import defaultdict

import boto3
from botocore.exceptions import ClientError

from cloud.cloud import Cloud


class AWS(Cloud):
    def __init__(self, **kwargs):
        super().__init__()
        self.client = self._connect(kwargs)

    def _connect(self, **kwargs):
        # Check if a profile is provided
        if kwargs.get('profile'):
            session = boto3.Session(profile_name=kwargs.get('profile'))
            return session.client("iam")

        # Check if access key and secret key are provided
        if kwargs.get('access_key') and kwargs.get('secret_key'):
            return boto3.client("iam", kwargs.get('access_key'), kwargs.get('secret_key'))

        # Fallback to environment variables
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

        if aws_access_key_id and aws_secret_access_key:
            return boto3.client("iam", aws_access_key_id, aws_secret_access_key)

        # No credentials found
        return None

    def start(self):
        data = defaultdict(lambda: {"Policy": []})
        try:
            res = self.client.get_account_authorization_details()
            account_id = self.client.get_user()["User"]["Arn"].split("::")[1].split(":")[0]
            self.logger.debug(f"Get all policy from account {account_id}")
            for user in res['UserDetailList']:
                arn = user["Arn"]
                try:
                    policies = user['AttachedManagedPolicies']
                except KeyError:
                    policies = []
                for policy in policies:
                    policy_arn = policy["PolicyArn"]
                    try:
                        if re.match(r"arn:aws:iam::\d+:policy/.*", policy_arn):
                            policy_version = self.client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
                            policy_document = \
                                self.client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)["PolicyVersion"][
                                    "Document"]
                            data[arn]["Policy"].append({policy_arn: policy_document["Statement"]})
                        else:
                            data[arn]["Policy"].append({policy_arn: policy_arn})
                    except ClientError as e:
                        print(f"Error while processing policy {policy_arn}: {str(e)}")
                    except Exception as e:
                        print(f"Unexpected error while processing policy {policy_arn}: {str(e)}")
        except ClientError as e:
            print(f"Error while connecting to AWS: {str(e)}")
        except Exception as e:
            print(f"Unexpected error while connecting to AWS: {str(e)}")
        return data
