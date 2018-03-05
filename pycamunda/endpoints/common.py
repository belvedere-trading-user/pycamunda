"""@ingroup endpoints
@file
Common schema definitions shared across multiple endpoint types.
"""
from enum import Enum, IntEnum

from dateutil.parser import parse
from voluptuous import Schema

from pycamunda.entity import JsonEntity, Number

## A schema validator for Camunda timestamp objects.
Timestamp = parse # pylint: disable=invalid-name

class ContentType(Enum):
    """Models HTTP content types.
    """
    OctetStream = 'application/octet-stream'
    Plain = 'text/plain'

class SortOrder(Enum):
    """Models sorting orders for REST queries.
    """
    Ascending = 'asc'
    Descending = 'desc'

class ResourceType(IntEnum):
    """Models the integer representation of Camunda resource types.
    @see https://docs.camunda.org/manual/7.8/user-guide/process-engine/authorization-service/#resources
    """
    Application = 0
    Authorization = 4
    Batch = 13
    DecisionDefinition = 10
    DecisionRequirementsDefinition = 14
    Deployment = 9
    Filter = 5
    Group = 2
    GroupMembership = 3
    ProcessDefinition = 6
    ProcessInstance = 8
    Task = 7
    Tenant = 11
    TenantMembership = 12
    User = 1

class Count(JsonEntity):
    """Models a count of Camunda objects.

    Many different Camunda endpoints return simple counts; these should all return the Count type.
    """
    @property
    def schema(self):
        return Schema({'count': Number}, required=True)
