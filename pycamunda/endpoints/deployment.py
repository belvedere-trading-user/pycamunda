"""@ingroup endpoints
@file
Definitions of Camunda Deployment REST endpoints.
"""
from voluptuous import Any, Coerce, Schema, Optional

from pycamunda.connector import GetEndpoint, PostEndpoint, DeleteEndpoint
from pycamunda.entity import JsonEntity, JsonInputEntity, Number, Text, Identifier, MultipartFormInput, FormOption
from .common import Count, SortOrder, Timestamp

class DeploymentListParameters(JsonInputEntity):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/deployment/get-query/#query-parameters
    """
    @property
    def schema(self):
        return Schema({
            'id': Text,
            'name': Text,
            'nameLike': Text,
            'source': Text,
            'withoutSource': True,
            'tenantIdIn': Text,
            'withoutTenantId': True,
            'includeDeploymentsWithoutTenantId': True,
            'after': Timestamp,
            'before': Timestamp,
            'sortBy': Any('id', 'name', 'deploymentTime', 'tenantId'),
            'sortOrder': Coerce(SortOrder),
            'firstResult': Number,
            'maxResults': Number
        })

class Deployment(JsonEntity):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/deployment/get-query/#result
    """
    @property
    def schema(self):
        return Schema({
            'id': Identifier,
            'name': Identifier,
            'source': Identifier,
            'deploymentTime': Timestamp,
            Optional('tenantId'): Identifier,
            Optional('links'): [Text]
        }, required=True)

class DeploymentList(JsonEntity):
    """Models a list of Deployment instances.
    """
    @property
    def schema(self):
        return Schema([Coerce(Deployment)])

class GetDeployments(GetEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/deployment/get-query/
    """
    @property
    def parameters_type(self):
        return DeploymentListParameters

    @property
    def uri(self):
        return '/deployment'

    @property
    def return_type(self):
        return DeploymentList

class GetDeploymentCount(GetEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/deployment/get-query-count/
    """
    @property
    def parameters_type(self):
        return DeploymentListParameters

    @property
    def uri(self):
        return '/deployment/count'

    @property
    def return_type(self):
        return Count

class GetDeployment(GetEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/deployment/get/
    """
    def __init__(self, deployment_id, engine_name=None):
        super(GetDeployment, self).__init__(engine_name=engine_name)
        self.deployment_id = deployment_id

    @property
    def uri(self):
        return '/deployment/{}'.format(self.deployment_id)

    @property
    def return_type(self):
        return Deployment

class NewDeploymentRequest(MultipartFormInput):
    """@see https://docs.camunda.org/manual/7.5/reference/rest/deployment/post-deployment/#request-body
    """
    @property
    def options_by_name(self):
        return {'deployment-name': FormOption(),
                'enable-duplicate-filtering': FormOption(),
                'deploy-changed-only': FormOption(),
                'deployment-source': FormOption(),
                'tenant-id': FormOption()}

class CreateDeployment(PostEndpoint):
    """@see https://docs.camunda.org/manual/7.8/reference/rest/deployment/post-deployment/
    """
    @property
    def uri(self):
        return '/deployment/create'

    @property
    def return_type(self):
        return Deployment

class RedeployRequest(JsonInputEntity):
    """@see https://docs.camunda.org/manual/7.5/reference/rest/deployment/post-redeploy-deployment/#request-body
    """
    @property
    def schema(self):
        return Schema({
            'resourceIds': [Text],
            'resourceNames': [Text],
            'source': Text
        })

class Redeploy(PostEndpoint):
    """@see https://docs.camunda.org/manual/7.5/reference/rest/deployment/post-redeploy-deployment/
    """
    def __init__(self, deployment_id, engine_name=None):
        super(Redeploy, self).__init__(engine_name=engine_name)
        self.deployment_id = deployment_id

    @property
    def uri(self):
        return '/deployment/{}/redeploy'.format(self.deployment_id)

    @property
    def return_type(self):
        return Deployment

class DeploymentResource(JsonEntity):
    """@see https://docs.camunda.org/manual/7.5/reference/rest/deployment/get-resources/#result
    """
    @property
    def schema(self):
        return Schema({
            'id': Identifier,
            'name': Text,
            'deploymentId': Identifier
        }, required=True)

class DeploymentResourceList(JsonEntity):
    """Models a list of DeploymentResource instances.
    """
    @property
    def schema(self):
        return Schema([Coerce(DeploymentResource)])

class GetDeploymentResources(GetEndpoint):
    """@see https://docs.camunda.org/manual/7.5/reference/rest/deployment/get-resources/
    """
    def __init__(self, deployment_id, engine_name=None):
        super(GetDeploymentResources, self).__init__(engine_name=engine_name)
        self.deployment_id = deployment_id

    @property
    def uri(self):
        return '/deployment/{}/resources'.format(self.deployment_id)

    @property
    def return_type(self):
        return DeploymentResourceList

class GetDeploymentResource(GetEndpoint):
    """@see https://docs.camunda.org/manual/7.5/reference/rest/deployment/get-resource/
    """
    def __init__(self, deployment_id, resource_id, engine_name=None):
        super(GetDeploymentResource, self).__init__(engine_name=engine_name)
        self.deployment_id = deployment_id
        self.resource_id = resource_id

    @property
    def uri(self):
        return '/deploymeny/{}/resources/{}'.format(self.deployment_id, self.resource_id)

    @property
    def return_type(self):
        return DeploymentResource

class DeploymentDeletionRequest(JsonInputEntity):
    """@see https://docs.camunda.org/manual/7.5/reference/rest/deployment/delete-deployment/#query-parameters
    """
    @property
    def schema(self):
        return Schema({
            'cascade': bool,
            'skipCustomListeners': bool
        })

class DeleteDeployment(DeleteEndpoint):
    """@see https://docs.camunda.org/manual/7.5/reference/rest/deployment/delete-deployment/
    """
    def __init__(self, deployment_id, engine_name=None):
        super(DeleteDeployment, self).__init__(engine_name=engine_name)
        self.deployment_id = deployment_id

    @property
    def parameters_type(self):
        return DeploymentDeletionRequest

    @property
    def uri(self):
        return '/deployment/{}'.format(self.deployment_id)
