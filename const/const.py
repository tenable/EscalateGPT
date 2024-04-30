AZURE_PLATFORM = "Azure"
AWS_PLATFORM = "AWS"

AZURE_URLS = {"users": "https://graph.microsoft.com/beta/users",
              "groups": "https://graph.microsoft.com/beta/groups",
              "member_of": "https://graph.microsoft.com/v1.0/{}/{}/memberOf",
              "groups_owners": "https://graph.microsoft.com/v1.0/groups/{}/owners"}

LOGIN_URL = "https://login.microsoftonline.com/{}"
RESOURCE = "https://graph.microsoft.com"
CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
AZURE_ENTITIES_TO_COLLECT = ["users", "groups"]

PROMPTS = {AZURE_PLATFORM: """Identify potential privilege escalation paths in an Entra ID environment based on the given 2 JSON data one for users and one for groups.
In the user JSON the key is User SPN and the value is where the user is a member of (groups and directory roles)
In the group JSON the key is the group name and the value is the owners of the group
If I give you a source user and/or a target user then I want you to find path that start at the source and end in target user only.
Generate output in the specified JSON format:
"paths": 
{{
[
        "Source User": "SourceUserName",
        "Action": "[ACTION] (The action the source can do to get to the target, if the source needs more then one action put it in a list)"
        "Target User": "TargetUserName,
        "Description": "Explanation of why this escalation is possible",
        "Mitigation": "Suggestions for preventing this escalation",
        "Other_Users": "If we have others users with the same permission write here there SPN"
    ...
]
}}
When analyzing privilege escalation paths:
- Consider both direct escalations and potential indirect multi-step attacks
- Aggregate users with identical escalation capabilities
- Offer technically accurate and detailed explanations
- Propose practical mitigation measures
Your output should be only the JSON!! without any additional information.
User data JSON: {users}
Group owner data JSON: {groups}
""",
           AWS_PLATFORM:
               """Identify potential privilege escalation paths based on the provided AWS policies.
List users who can gain unauthorized access to another's account, considering actions beyond direct access.
Present the findings in JSON format, including paths, policy actions, associated risks, mitigations, and identify users with similar permissions.
If I give you a source user and/or a target user then I want you to find path that start at the source and end in target user only.
When analyzing privilege escalation paths:
- Consider both direct escalations and potential indirect multi-step attacks
- Aggregate users with identical escalation capabilities
- Offer technically accurate and detailed explanations
- Propose practical mitigation measures
Generate output in the specified JSON format:

"paths": 
[
"Source User": "Name of the source username",
"PolicyName": "[PolicyAction]",
"PolicyAction": "[PolicyAction]",
"Target User": "Name of the target username,
"Description": "Explanation of why this escalation is possible",
"Mitigation": "Suggestions for preventing this escalation",
"Other_Users": "If we have others users with the same permission write here there SPN"
...
]
}}       
Policies:{}
"""}
