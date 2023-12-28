AZURE_URLS = {"users": "https://graph.microsoft.com/beta/users",
              "groups": "https://graph.microsoft.com/beta/groups",
              "member_of": "https://graph.microsoft.com/v1.0/{}/{}/memberOf",
              "groups_owners": "https://graph.microsoft.com/v1.0/groups/{}/owners"}
USERS_URL = "https://graph.microsoft.com/beta/users"
USER_MEMBER_OF = "https://graph.microsoft.com/v1.0/users/{}/memberOf"
GROUPS_URL = "https://graph.microsoft.com/beta/groups"
GROUPS_OWNER_URL = "https://graph.microsoft.com/v1.0/groups/{}/owners"

LOGIN_URL = "https://login.microsoftonline.com/{}"
RESOURCE = "https://graph.microsoft.com"
CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"

AZURE_PROMPT = """List all users that can gain access to another's account (
            privilege escalation) based on the data provided below.
            The data is in json format that the key is userPrincipalName and the value is all the group and directory role that the user is member of.
            In addition I will give you another json that the key is group name and the value is all the owners of the group.
            You can think of ways that users can perform 
            actions after they gain access to another user and not only directly. 
            Write the response in paths ways.
            The path format is: "[SourceUserName]-[ACTION]->[TargetUserName]" 
            Include a description why this path is possible (risk) and how to fix (mitigation) it. 
            Please output as a JSON format as followed: 
            DATA:\n{}"""


AWS_PROMPT = """List all users that can gain access to another's account (
            privilege escalation) based on the policies provided below. You can think of ways that users can perform 
            actions after they gain access to another user and not only directly. 
            Write the response in paths ways and in case of *, show only one path indicating *.
            The path format is: "[SourceUserName]-[PolicyAction]->[TargetUserName]" 
            Include a description why this path is possible (risk) and how to fix (mitigation) it. 
            Please output as a JSON format as followed: {["path": path, "policy": PolicyAction, "risk": risk, "mitigation": mitigation]}
            Policies:\n"""
