AZURE_URLS = {"users": "https://graph.microsoft.com/beta/users",
              "groups": "https://graph.microsoft.com/beta/groups",
              "member_of": "https://graph.microsoft.com/v1.0/{}/{}/memberOf",
              "groups_owners": "https://graph.microsoft.com/v1.0/groups/{}/owners"}

LOGIN_URL = "https://login.microsoftonline.com/{}"
RESOURCE = "https://graph.microsoft.com"
CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"

AZURE_PROMPT = """
List all Azure users that can gain access to another Azure user's permissions (privilege escalation) based on the JSON data below. Provide output in the following JSON format:
  "paths": [
      "path": "[SourceUserName]-[ACTION]->[TargetUserName]",
      "description": "Explanation of why this escalation is possible", 
      "mitigation": "Suggestions for preventing this escalation"
    ...
  ]

When identifying privilege escalation paths:
- Consider both direct escalations and indirect multi-step attacks 
- Combine users with identical escalation capabilities  
- Provide technically accurate and detailed explanations
- Suggest practical mitigation measures 

User data JSON:
{}
Group owner data JSON: 
{}
"""

AWS_PROMPT = """List all users that can gain access to another's account (
            privilege escalation) based on the policies provided below. You can think of ways that users can perform 
            actions after they gain access to another user and not only directly. 
            Write the response in paths ways and in case of *, show only one path indicating *.
            The path format is: "[SourceUserName]-[PolicyAction]->[TargetUserName]" 
            Include a description why this path is possible (risk) and how to fix (mitigation) it. 
            Please output as a JSON format as followed: {["path": path, "policy": PolicyAction, "risk": risk, "mitigation": mitigation]}
            Policies:\n"""
