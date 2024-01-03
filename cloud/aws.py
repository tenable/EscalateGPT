import os
import re
import sys
from collections import defaultdict

import boto3
import botocore
from botocore.exceptions import ClientError

from cloud.cloud import Cloud


class AWS(Cloud):
    def __init__(self, args):
        super().__init__()
        if args.profile:
            self.client = self._connect(profile=args.profile)
        elif args.aws_key and args.aws_secret:
            self.client = self._connect(aws_key=args.aws_key, aws_secret=args.aws_secret)
        elif os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            self._connect()
        else:
            self.logger.error("There is no credentials to connect AWS")
            sys.exit(0)

    def _connect(self, **kwargs):
        try:
            # Check if a profile is provided
            if kwargs.get('profile'):
                self.logger.debug(
                    f"Try to establishing connection to AWS' using the profile {kwargs.get('profile')}")
                session = boto3.Session(profile_name=kwargs.get('profile'))
                return session.client("iam")

            # Check if access key and secret key are provided
            if kwargs.get('aws_key') and kwargs.get('aws_secret'):
                self.logger.debug(
                    f"Try to establishing connection to AWS' using AWS key and AWS secret")
                return boto3.client("iam", aws_access_key_id=kwargs.get('aws_key'), aws_secret_access_key=kwargs.get('aws_secret'))

            # Fallback to environment variables
            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
            aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

            if aws_access_key_id and aws_secret_access_key:
                self.logger.debug(
                    f"Try to establishing connection to AWS' using environment variable")
                return boto3.client("iam", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        except Exception as e:
            self.logger.error(f"Error while try to connect AWS {e}")
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
                                self.client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)[
                                    "PolicyVersion"][
                                    "Document"]
                            data[arn]["Policy"].append({policy_arn: policy_document["Statement"]})
                        else:
                            data[arn]["Policy"].append({policy_arn: policy_arn})
                    except ClientError as e:
                        self.logger.error(f"Error while processing policy {policy_arn}: {str(e)}")
                    except Exception as e:
                        self.logger.error(f"Unexpected error while processing policy {policy_arn}: {str(e)}")
        except ClientError as e:
            self.logger.error(f"Error while connecting to AWS: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error while connecting to AWS: {str(e)}")
        return data
