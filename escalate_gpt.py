import argparse
from collections import defaultdict
from botocore.exceptions import ClientError
import boto3
import openai
import json
import re


def get_policies(aws_access_key_id: str = None, aws_secret_access_key: str = None):
    data = defaultdict(lambda: {"Policy": []})
    try:
        if aws_access_key_id and aws_secret_access_key:
            iam = boto3.client('iam', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        else:
            iam = boto3.client('iam')
        res = iam.get_account_authorization_details()
        account_id = iam.get_user()["User"]["Arn"].split("::")[1].split(":")[0]
        print(f"Get all policy from account {account_id}")
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
                        policy_version = iam.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
                        policy_document = \
                            iam.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)["PolicyVersion"][
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


def ask_chat_gpt(prompt, model):
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": """List all users that can gain access to another's account (
            privilege escalation) based on the policies provided below. You can think of ways that users can perform 
            actions after they gain access to another user and not only directly. 
            Write the response in paths ways and in case of *, show only one path indicating *.
            The path format is: "[SourceUserName]-[PolicyAction]->[TargetUserName]" 
            Include a description why this path is possible (risk) and how to fix (mitigation) it. 
            Please output as a JSON format as followed: {["path": path, "policy": PolicyAction, "risk": risk, "mitigation": mitigation]}
            Policies:
            """ + json.dumps(prompt)}])
        message = json.loads(completion.get('choices')[0].get('message').get('content').replace("\n\n", ""))
        print(json.dumps(message, indent=4))
    except openai.error.AuthenticationError as e:
        print("OpenAI API Key is invalid. Please check for a new key")
        return
    except Exception as e:
        print(f"Unexpected error while try to get OpenAI answer\n {e}")


if __name__ == '__main__':
    print("""    #    #     #  #####                                 #####  ######  ####### 
   # #   #  #  # #     #     ####  #    #   ##   ##### #     # #     #    #    
  #   #  #  #  # #          #    # #    #  #  #    #   #       #     #    #    
 #     # #  #  #  #####     #      ###### #    #   #   #  #### ######     #    
 ####### #  #  #       #    #      #    # ######   #   #     # #          #    
 #     # #  #  # #     #    #    # #    # #    #   #   #     # #          #    
 #     #  ## ##   #####      ####  #    # #    #   #    #####  #          #    
                                                                               """)
    parser = argparse.ArgumentParser(description='AWS privilege escalation tool using ChatGPT')
    parser.add_argument('-aws_key', type=str, help='AWS access key', required=False)
    parser.add_argument('-aws_secret', type=str, help='AWS secret key', required=False)
    parser.add_argument('-openai_key', type=str, help='API Key for OpenAI', required=True)
    parser.add_argument('--chatgpt_model', type=str, default='gpt-4', help='ChatGPT model version')
    args = parser.parse_args()

    openai.api_key = args.openai_key
    chatgpt_model = args.chatgpt_model
    aws_key = args.aws_key
    aws_secret = args.aws_secret

    print("Starting AWS privilege escalation tool using ChatGPT")
    policies = get_policies(aws_key, aws_secret)
    print(f"Found {len(policies)} policies in use. Prompting ChatGPT for analysis")
    ask_chat_gpt(policies, chatgpt_model)
