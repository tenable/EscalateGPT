import json
from dataclasses import dataclass
from typing import Optional, List

import requests
from adal import AuthenticationContext, AdalError

from cloud.cloud import Cloud
from const.const import RESOURCE, LOGIN_URL, CLIENT_ID, AZURE_URLS, AZURE_ENTITIES_TO_COLLECT, PROMPTS


@dataclass
class Role:
    role_name: Optional[str] = None
    description: Optional[str] = None
    role_template_id: Optional[str] = None


@dataclass
class Group:
    group_name: Optional[str] = None
    description: Optional[str] = None
    owners: Optional[List[str]] = None


class Azure(Cloud):
    def __init__(self, username: str, password: str, tenant_id: str):
        super().__init__()
        self.username = username
        self.password = password
        self.tenant_id = tenant_id
        self._graph_headers = {"Authorization": f"Bearer {self._connect()}",
                               "Content-Type": "application/json"}

    def _connect(self, **kwargs) -> str:
        """
            Establishes a connection to Azure Active Directory (Azure AD) and retrieves an access token.

            This method uses the provided Azure AD credentials (username, password) to authenticate and acquire
            an access token for the specified resource. It handles common Azure AD error responses and raises
            specific ValueErrors with meaningful messages.
            @return: Access token for the specified resource in Azure AD.
            @rtype: str

            Raises:
            - ValueError: If authentication fails due to invalid credentials, expired password, or disabled account.
            - ValueError: If an unexpected error occurs during the authentication process.

            Example usage:
                access_token = _connect(username='your_username', password='your_password')
            """
        self.logger.debug(
            f"Try to establishing connection to resource {RESOURCE} in 'Azure AD'  with user {self.username}")
        try:
            auth_context = AuthenticationContext(LOGIN_URL.format(self.tenant_id))
            return auth_context.acquire_token_with_username_password(RESOURCE, self.username, self.password,
                                                                     CLIENT_ID).get('accessToken')
        except AdalError as e:
            if e.error_response:
                if "AADSTS50126" in e.error_response['error_description']:
                    raise ValueError("Error validating credentials due to invalid username or password.")
                elif "AADSTS50055" in e.error_response['error_description']:
                    raise ValueError("The password of the user is expired.")
                elif "AADSTS50057" in e.error_response['error_description']:
                    raise ValueError("The user account is disabled.")
            else:
                raise ValueError(f"Error while try connect to AZURE {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error while authenticating to 'Azure AD'\n{e}")

    def start(self) -> str:
        """
         Collects information about users, groups, and roles in Azure Active Directory for generating a prompt.
         This method gathers details about all users and the groups and roles they are members of in Azure Active Directory.
         It constructs a dictionary containing user information, along with the groups and roles each user is a member of.
         The generated prompt is formatted using the collected data.

         @return: Prompt to be sent to OpenAI containing information about Azure Active Directory entities.
         @rtype: str
         """
        data_for_open_ai = {}
        self.logger.debug(f"Start to collect user and groups from AzureAD")
        for entity_type in AZURE_ENTITIES_TO_COLLECT:
            data_for_open_ai[entity_type] = {}
            for entity in self._get_entities_details(entity_type):
                all_groups_and_roles = []
                entity_group_and_roles = self._get_groups_and_roles_entity_is_member_of(entity_type, entity['id'])
                for group_or_role in entity_group_and_roles:
                    if group_or_role['@odata.type'] == '#microsoft.graph.directoryRole':
                        all_groups_and_roles.append(
                            Role(role_name=group_or_role['displayName'], description=group_or_role['description'],
                                 role_template_id=group_or_role['roleTemplateId']).__dict__)
                    else:
                        all_groups_and_roles.append(
                            Group(group_name=group_or_role['displayName'], description=group_or_role['description'],
                                  owners=self._get_group_owners(group_id=entity['id'])).__dict__)
                entity_name = entity.get('userPrincipalName') if entity.get(
                    'userPrincipalName') else entity.get('displayName')
                data_for_open_ai[entity_type][entity_name] = all_groups_and_roles
        return PROMPTS["AZURE"].format(json.dumps(data_for_open_ai[AZURE_ENTITIES_TO_COLLECT[0]]),
                                       json.dumps(data_for_open_ai[AZURE_ENTITIES_TO_COLLECT[1]]))

    def _get_entities_details(self, entity: str) -> dict:
        """
          Sends a request to retrieve details about users or groups from Azure Active Directory.
          This method sends an HTTP GET request to the Azure Active Directory Graph API to fetch information
          about either users or groups. It expects the entity parameter to be 'users' or 'groups'.

          @param entity: The type of entity for which details are to be retrieved ('users' or 'groups').
          @type entity: str

          @return: A dictionary containing data about the requested users/groups.
          @rtype: dict
          """
        res = requests.get(AZURE_URLS[entity], headers=self._graph_headers).json()
        if "error" in res:
            self.logger.error(f"Failed to get {entity}\nerror {res['error']['message']}")
            return {}
        return res['value']

    def _get_groups_and_roles_entity_is_member_of(self, entity: str, entity_id: str) -> dict:
        """
        Checks all the memberships of a user or group in Azure Active Directory.
        This method sends an HTTP GET request to the Azure Active Directory Graph API to retrieve information
        about the groups and roles that a user or group with the specified entity ID is a member of.

        @param entity: The type of entity for which memberships are to be checked ('users' or 'groups').
        @type entity: str

        @param entity_id: The unique identifier of the entity whose memberships are being checked.
        @type entity_id: str

        @return: A dictionary containing data about the memberships of the specified user/group.
        @rtype: dict
        """
        res = requests.get(AZURE_URLS['member_of'].format(entity, entity_id), headers=self._graph_headers).json()
        if "error" in res:
            self.logger.error(f"Failed to get {entity} member_of \nerror {res['error']['message']}")
            return {}
        return res['value']

    def _get_group_owners(self, group_id: str) -> List[str]:
        """
        Retrieves the owners of a specified group in Azure Active Directory.
        This method sends an HTTP GET request to the Azure Active Directory Graph API to fetch information
        about the owners of the group with the specified group ID. It returns a list of userPrincipalName
        for each owner.

        @param group_id: The unique identifier of the group whose owners are to be retrieved.
        @type group_id: str

        @return: List of userPrincipalName for the owners of the group.
        @rtype: List[str]
        """
        list_owners = []
        res = requests.get(AZURE_URLS['groups_owners'].format(group_id), headers=self._graph_headers).json()
        if "error" in res:
            self.logger.error(f"Failed to get owners to group {group_id}\nerror {res['error']['message']}")
            return []
        for x in res['value']:
            if "user" in x["@odata.type"]:
                list_owners.append(x['userPrincipalName'])
        return list_owners
