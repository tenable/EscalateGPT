AZURE_URLS = {"users": "https://graph.microsoft.com/beta/users",
              "groups": "https://graph.microsoft.com/beta/groups",
              "member_of": "https://graph.microsoft.com/v1.0/{}/{}/memberOf",
              "groups_owners": "https://graph.microsoft.com/v1.0/groups/{}/owners"}

LOGIN_URL = "https://login.microsoftonline.com/{}"
RESOURCE = "https://graph.microsoft.com"
CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
AZURE_ENTITIES_TO_COLLECT = ["users", "groups"]

PROMPTS = {"AZURE": """Identify potential privilege escalation paths in an Azure environment based on the given 2 JSON data one for users and one for groups.
In the user JSON the key is User SPN and the value is where the user is a member of (groups and directory roles)
In the group JSON the key is the group name and the value is the owners of the group
Generate output in the specified JSON format:
"paths": 
{{
[
        "path": "[SourceUserName]-[ACTION (The action the source can do to get to the target)]->[TargetUserName]",
        "description": "Explanation of why this escalation is possible",
        "mitigation": "Suggestions for preventing this escalation",
        "all_users": "If we have others users with the same permission write here there SPN"
    ...
]
}}
When analyzing privilege escalation paths:
- Consider both direct escalations and potential indirect multi-step attacks
- Aggregate users with identical escalation capabilities
- Offer technically accurate and detailed explanations
- Propose practical mitigation measures
Your output should be only the JSON
User data JSON: {}
Group owner data JSON: {}
""",
           "AWS":
"""Identify potential privilege escalation paths based on the provided policies. List users who can gain unauthorized access to another's account, considering actions beyond direct access. Present the findings in JSON format, including paths, policy actions, associated risks, mitigations, and identify users with similar permissions.
Prompt Format:
List all privilege escalation paths as JSON objects, following the format:
{{"path": "[SourceUserName]-[PolicyAction]->[TargetUserName]", "policy": "PolicyAction", "risk": "Explain the risk associated with the path", "mitigation": "Provide mitigation steps to address the risk", "all_users": "List other users with similar permissions"}}

Policies:\n{}"""}
