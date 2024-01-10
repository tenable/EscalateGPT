import os
import re
import sys
import json
from collections import defaultdict

import boto3

from botocore.exceptions import ClientError

from cloud.cloud import Cloud
from const.const import PROMPTS


class AWS(Cloud):
    def __init__(self, args):
        super().__init__()
        if args.profile:
            self.client = self._connect(profile=args.profile)
        elif args.aws_key and args.aws_secret:
            self.client = self._connect(aws_key=args.aws_key, aws_secret=args.aws_secret)
        # Fallback to environment variables
        elif os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            self._connect(aws_key=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret=os.environ.get('AWS_SECRET_ACCESS_KEY'))
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
                return boto3.client("iam", aws_access_key_id=kwargs.get('aws_key'),
                                    aws_secret_access_key=kwargs.get('aws_secret'))
        except Exception as e:
            self.logger.error(f"Error while try to connect AWS {e}")
            return None

    def start(self) -> str:
        users_policies = defaultdict(lambda: {"Policy": []})
        try:
            aws_data = self.client.get_account_authorization_details()
            account_id = self._get_account_id()
            self.logger.debug(f"Get all policy from account {account_id}")
            for user in aws_data.get('UserDetailList'):
                for policy in user.get("AttachedManagedPolicies"):
                    policy_arn = policy["PolicyArn"]
                    try:
                        if re.match(r"arn:aws:iam::\d+:policy/.*", policy_arn):
                            policy_document = self._extract_policy_document(policy_arn)
                            users_policies[policy_arn]["Policy"].append({policy_arn: policy_document})
                        else:
                            users_policies[user["Arn"]]["Policy"].append({policy_arn: policy_arn})
                    except ClientError as e:
                        self.logger.error(f"Error while processing policy {policy_arn}: {e}")
                    except Exception as e:
                        self.logger.error(f"Unexpected error while processing policy {policy_arn}: {e}")
        except ClientError as e:
            self.logger.error(f"Error while connecting to AWS: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error while connecting to AWS: {e}")
        return PROMPTS['AWS'].format(json.dumps(users_policies))

    def _get_account_id(self):
        try:
            account_id = self.client.get_user()["User"]["Arn"].split("::")[1].split(":")[0]
        except Exception as e:
            self.logger.error(f"Error while try get account_id {e}")
            account_id = ""
        return account_id

    def _extract_policy_document(self, policy_arn):
        policy_version = self.client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
        policy_document = \
            self.client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)["PolicyVersion"]["Document"]
        return policy_document["Statement"]
