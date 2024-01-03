import requests
from adal import AuthenticationContext, AdalError

from cloud.cloud import Cloud
from static.static import RESOURCE, LOGIN_URL, CLIENT_ID, AZURE_URLS


class Azure(Cloud):
    def __init__(self, username: str, password: str, tenant_id: str):
        super().__init__()
        self.username = username
        self.password = password
        self.tenant_id = tenant_id
        self._graph_headers = {"Authorization": f"Bearer {self._connect()}",
                               "Content-Type": "application/json"}

    def _connect(self):
        """
            Retrieves an access token for the specified resource using the provided username and password.
            Args:
                resource (str, optional): The resource for which to acquire the access token. Defaults to "https://graph.microsoft.com".
            Returns:
                str: The access token.
            Raises:
                ValueError: If there is an error validating the credentials or an unexpected error occurs while authenticating.
            """
        self.logger.debug(
            f"Try to establishing connection to resource {RESOURCE} in 'Azure AD'  with user {self.username}")
        try:
            auth_context = AuthenticationContext(LOGIN_URL.format(self.tenant_id))
            return auth_context.acquire_token_with_username_password(RESOURCE, self.username, self.password,
                                                                     CLIENT_ID).get('accessToken')
        except AdalError as e:
            if "AADSTS50126" in e.error_response['error_description']:
                raise ValueError("Error validating credentials due to invalid username or password.")
            elif "AADSTS50055" in e.error_response['error_description']:
                raise ValueError("The password of the user is expired.")
            elif "AADSTS50057" in e.error_response['error_description']:
                raise ValueError("The user account is disabled.")
        except Exception as e:
            raise ValueError(f"Unexpected error while authenticating to 'Azure AD'\n{e}")

    def start(self):
        data_to_collect = ["users", "groups"]
        res = {}
        self.logger.debug(f"Collecting user and groups from AzureAD")
        for entity_name in data_to_collect:
            res[entity_name] = []
            for entity in self._get_entities(entity_name):
                groups_and_roles = []
                entity_data = self._get_entity_data(entity_name, entity['id'])
                for data in entity_data:
                    if data['@odata.type'] == '#microsoft.graph.directoryRole':
                        groups_and_roles.append({"RoleName": data['displayName'], 'Description': data['description'],
                                                 'RoleTemplateId': data['roleTemplateId']})
                    else:
                        groups_and_roles.append({"GroupName": data['displayName'], 'description': data['description'],
                                                 "owners": self._get_group_owners(group_id=entity['id'])})
                res[entity_name].append({entity.get('userPrincipalName') if entity.get(
                    'userPrincipalName') else entity.get('displayName'): groups_and_roles})
        return res

    def _get_entities(self, entity):
        res = requests.get(AZURE_URLS[entity], headers=self._graph_headers).json()
        if "error" in res:
            self.logger.error(f"Failed to get {entity}\nerror {res['error']['message']}")
            return {}
        return res['value']

    def _get_entity_data(self, entity: str, user_id: str):
        res = requests.get(AZURE_URLS['member_of'].format(entity, user_id), headers=self._graph_headers).json()
        if "error" in res:
            self.logger.error(f"Failed to get {entity} member_of \nerror {res['error']['message']}")
            return {}
        return res['value']

    def _get_group_owners(self, group_id: str):
        list_owners = []
        res = requests.get(AZURE_URLS['groups_owners'].format(group_id), headers=self._graph_headers).json()
        if "error" in res:
            self.logger.error(f"Failed to get owners to group {group_id}\nerror {res['error']['message']}")
            return {}
        for x in res['value']:
            if "user" in x["@odata.type"]:
                list_owners.append(x['userPrincipalName'])
        return list_owners