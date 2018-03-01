"""@ingroup endpoints
@file
Definitions of Camunda REST endpoints.
"""
from enum import IntEnum
from voluptuous import Any, Coerce, Schema, Optional

from pycamunda.connector import GetEndpoint, PostEndpoint, PutEndpoint, DeleteEndpoint
from pycamunda.entity import JsonEntity, JsonInputEntity, Number, Text, Identifier
from .common import Count, ResourceType, SortOrder

class AuthorizationType(IntEnum):
    """Models Camunda authorization type ids.
    """
    Global = 0
    Grant = 1
    Revoke = 2

class Authorization(JsonEntity):
    """Models a Camunda authorization object.

    @see https://docs.camunda.org/manual/7.8/reference/rest/authorization/get-query/#result
    """
    @property
    def schema(self):
        return Schema({
            'id': Text,
            'type': Coerce(AuthorizationType),
            'permissions': [Text],
            'userId': Identifier,
            'groupId': Identifier,
            'resourceType': Coerce(ResourceType),
            'resourceId': Identifier,
            Optional('links'): [Text]
        }, required=True)

class AuthorizationList(JsonEntity):
    """Models a list of Authorization instances.
    """
    @property
    def schema(self):
        return Schema([Coerce(Authorization)])

class AuthorizationListParameters(JsonInputEntity):
    """Models request parameters for a list of Authorization.

    @see https://docs.camunda.org/manual/7.8/reference/rest/authorization/get-query/#query-parameters
    """
    @property
    def schema(self):
        return Schema({
            'id': Text,
            'type': Coerce(AuthorizationType),
            'userIdIn': Text,
            'groupIdIn': Text,
            'resourceType': Coerce(ResourceType),
            'resourceId': Text,
            'sortBy': Any('resourceType', 'resourceId'),
            'sortOrder': Coerce(SortOrder),
            'firstResult': Number,
            'maxResults': Number
        })

class GetAuthorizations(GetEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/authorization/get-query/
    """
    @property
    def parameters_type(self):
        return AuthorizationListParameters

    @property
    def uri(self):
        return '/authorization'

    @property
    def return_type(self):
        return AuthorizationList

class AuthorizationCountParameters(JsonInputEntity):
    """Models request parameters for a list of Authorization.

    @see https://docs.camunda.org/manual/7.8/reference/rest/authorization/get-query/#query-parameters
    """
    @property
    def schema(self):
        return Schema({
            'id': Text,
            'type': Coerce(AuthorizationType),
            'userIdIn': Text,
            'groupIdIn': Text,
            'resourceType': Coerce(ResourceType),
            'resourceId': Text,
        })

class GetAuthorizationCount(GetEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/authorization/get-query-count/
    """
    @property
    def parameters_type(self):
        return AuthorizationCountParameters

    @property
    def uri(self):
        return '/authorization/count'

    @property
    def return_type(self):
        return Count

class GetAuthorization(GetEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/authorization/get/
    """
    def __init__(self, authorization_id, engine_name=None):
        super(GetAuthorization, self).__init__(engine_name=engine_name)
        self.authorization_id = authorization_id

    @property
    def uri(self):
        return '/authorization/{}'.format(self.authorization_id)

    @property
    def return_type(self):
        return Authorization

class AuthorizationCheckParameters(JsonInputEntity):
    """Models request parameters for CheckAuthorization.
    """
    @property
    def schema(self):
        return Schema({
            'permissionName': Text,
            'permissionValue': Text,
            'resourceName': Text,
            'resourceType': Coerce(ResourceType),
            Optional('resourceId'): Text
        }, required=True)

class AuthorizationCheckResult(JsonEntity):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/authorization/get-check/#result
    """
    @property
    def schema(self):
        return Schema({
            'permissionName': Text,
            'resourceName': Text,
            'resourceId': Identifier,
            'isAuthorized': bool
        }, required=True)

class CheckAuthorization(GetEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/authorization/get-check/
    """
    @property
    def parameters_type(self):
        return AuthorizationCheckParameters

    @property
    def parameters_required(self):
        return True

    @property
    def uri(self):
        return '/authorization/check'

    @property
    def return_type(self):
        return AuthorizationCheckResult

class NewAuthorizationRequest(JsonInputEntity):
    """The request body for the CreateAuthorization and UpdateAuthorization endpoints.

    The "type" key is required for CreateAuthorization, but not accepted for UpdateAuthorization.
    """
    @property
    def schema(self):
        return Schema({
            Optional('type'): Coerce(AuthorizationType),
            'permissions': [Text],
            'userId': Identifier,
            'groupId': Identifier,
            'resourceType': Coerce(ResourceType),
            'resourceId': Identifier
        }, required=True)

class CreateAuthorization(PostEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/authorization/post-create/
    """
    @property
    def uri(self):
        return '/authorization/create'

    @property
    def return_type(self):
        return Authorization

class UpdateAuthorization(PutEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/authorization/put-update/
    """
    def __init__(self, authorization_id, engine_name=None):
        super(UpdateAuthorization, self).__init__(engine_name=engine_name)
        self.authorization_id = authorization_id

    @property
    def uri(self):
        return '/authorization/{}'.format(self.authorization_id)

class DeleteAuthorization(DeleteEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/authorization/delete/
    """
    def __init__(self, authorization_id, engine_name=None):
        super(DeleteAuthorization, self).__init__(engine_name=engine_name)
        self.authorization_id = authorization_id

    @property
    def uri(self):
        return '/authorization/{}'.format(self.authorization_id)
