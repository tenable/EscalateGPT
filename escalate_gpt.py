import argparse

from cloud.aws import AWS
from cloud.azure import Azure
from gpt_client.gpt_client import GPTClient


def parse_args():
    parser = argparse.ArgumentParser(description="Script to do something with OpenAPI")

    # Required arguments
    parser.add_argument("OpenAPIKey", type=str, help="OpenAPI Key")

    # Optional arguments
    parser.add_argument("--model", type=str, default="gpt-4-1106-preview", help="OpenAPI Model (default: gpt4-turbo)")
    parser.add_argument("--temperature", type=float, default=0.1, help="OpenAPI Temperature (default: 0.1)")

    # Platform selection
    parser.add_argument("--platform", choices=["AWS", "AZURE"], required=True, help="Platform (AWS or AZURE)")

    # Platform-specific arguments
    aws_group = parser.add_argument_group("AWS Options")
    aws_group.add_argument("-k", "--aws-key", type=str, help="AWS Key")
    aws_group.add_argument("-s", "--aws-secret", type=str, help="AWS Secret")
    aws_group.add_argument("-P", "--profile", help='AWS CLI profile name')

    azure_group = parser.add_argument_group("Azure Options")
    azure_group.add_argument("-u", "--username", type=str, help="Azure Username")
    azure_group.add_argument("-p", "--password", type=str, help="Azure Password")
    azure_group.add_argument("-t", "--tenant-id", type=str, help="Azure Tenant ID")

    return parser.parse_args()


def main():
    args = parse_args()
    if args.platform == "AZURE":
        client = Azure(username=args.username, password=args.password, tenant_id=args.tenant_id)
    else:
        client = AWS(args=args)
    openai = GPTClient(openai_key=args.OpenAPIKey, model=args.model, temperature=args.temperature)
    prompt = client.start()
    client.logger.debug("Finish to get all data send to OPENAI for analyze")
    openai_answer = openai.ask(prompt)
    client.logger.debug(openai_answer)


if __name__ == '__main__':
    main()


