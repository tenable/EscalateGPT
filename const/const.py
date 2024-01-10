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
               """List all users that can gain access to another's account (
                       privilege escalation) based on the policies provided below. You can think of ways that users can perform 
                       actions after they gain access to another user and not only directly. 
                       Write the response in paths ways and in case of *, show only one path indicating *.
                       The path format is: "[SourceUserName]-[PolicyAction]->[TargetUserName]" 
                       Include a description why this path is possible (risk) and how to fix (mitigation) it. 
                       Please output as a JSON format as followed: {{["path": path, "policy": PolicyAction, "risk": risk, "mitigation": mitigation, "all_users": "If we have others users with the same permission write here there name"]}}
                       Policies:\n{}"""}
