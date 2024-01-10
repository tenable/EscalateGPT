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
        The function collect all users and the groups and roles they are memebers of.
        @return: Prompt we want to send to OPEN_AI
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
        Function send request to get data about the users/groups
        @param entity: can be users or groups
        @type entity:  str
        @return: dict with data on users/groups
        @rtype: dict
        """
        res = requests.get(AZURE_URLS[entity], headers=self._graph_headers).json()
        if "error" in res:
            self.logger.error(f"Failed to get {entity}\nerror {res['error']['message']}")
            return {}
        return res['value']

    def _get_groups_and_roles_entity_is_member_of(self, entity: str, entity_id: str) -> dict:
        """
        Function check for all the membership of the user/group
        @param entity: can be users or groups
        @type entity: str
        @param entity_id: the entity id
        @type entity_id: str
        @return: dict with the membership of users/groups
        @rtype: dict
        """
        res = requests.get(AZURE_URLS['member_of'].format(entity, entity_id), headers=self._graph_headers).json()
        if "error" in res:
            self.logger.error(f"Failed to get {entity} member_of \nerror {res['error']['message']}")
            return {}
        return res['value']

    def _get_group_owners(self, group_id: str) -> List[str]:
        """
        Function check for owners of group
        @param group_id:  The group id
        @type group_id: str
        @return: List of the owners of the group
        @rtype: List of userPrincipalName
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
