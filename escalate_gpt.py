import argparse
from const.const import AWS_PLATFORM, AZURE_PLATFORM
from ai_client.anthropic_client import AnthropicClient
from ai_client.gpt_client import OpenAIClient
from cloud.aws import AWS
from cloud.azure import Azure


def parse_args():
    parser = argparse.ArgumentParser(description="EscalateGPT privilege escalation tool for cloud")

    # LLM arguments
    llm_group = parser.add_argument_group("LLM Options")
    llm_group.add_argument("--api_key", type=str, help="LLM Key", required=True)
    llm_group.add_argument("--llm_vendor", type=str, help="LLM vendor", required=True, choices=['Anthropic', 'OpenAI'])
    llm_group.add_argument("--model", type=str, help="LLM Model")
    llm_group.add_argument("--temperature", type=float, default=0.1, help="LLM Temperature (default: 0.1)")

    # Platform selection
    parser.add_argument("--platform", choices=[AWS_PLATFORM, AZURE_PLATFORM], required=True,
                        help="Platform (AWS or Azure)")

    parser.add_argument("--source_user", type=str, help="The source user of the path", default="")
    parser.add_argument("--target_user", type=str, help="The source user of the path", default="")
    parser.add_argument("--additional_info", type=str, help="More info for the LLM", default="")

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
    user_args = parse_args()
    set_default_model(user_args)

    client = globals()[f"{user_args.platform}"](user_args)
    llm = globals()[f"{user_args.llm_vendor}Client"](apikey=user_args.api_key, model=user_args.model,
                                                     temperature=user_args.temperature)
    prompt = client.start()
    prompt = f"{prompt}SourceUserName:{user_args.source_user}\nTargetUserName:{user_args.target_user}\nAdditionalInformation:{user_args.additional_info}"

    client.logger.debug(
        f"All the data we need for analysis has been collected.\nwe will be sent to {user_args.llm_vendor} for analysis.")
    llm_answer = llm.ask(prompt)
    try:
        with open("PrivilegeEscalationPaths.json", "w") as fh:
            client.logger.debug("Writing result to PrivilegeEscalationPaths file.")
            fh.write(llm_answer)
    except Exception as e:
        raise Exception(f"Error writing privilege escalation path {e}")


def set_default_model(user_args):
    if not user_args.model:
        if user_args.llm_vendor == "Anthropic":
            user_args.model = "claude-3-opus-20240229"
        else:
            user_args.model = "gpt-4-1106-preview"


if __name__ == '__main__':
    main()
