"""@ingroup pycamunda
@file
Definitions of the entity representations for data used as input to/output from the Camunda api.
"""
import json
import logging
import sys
from abc import ABCMeta, abstractproperty, abstractmethod
from collections import Mapping

import voluptuous

log = logging.getLogger(__name__)

## A schema validator for arbitrary numeric types.
Number = voluptuous.Any(int, long, float) #pylint: disable=invalid-name

## A schema validator for arbitrary textual types.
Text = voluptuous.Any(str, unicode) #pylint: disable=invalid-name

## A schema validator for Camunda identifiers.
Identifier = voluptuous.Any(Text, None) #pylint: disable=invalid-name

class MalformedEntity(Exception):
    """Raised if a raw api response cannot be parsed into an intermediate format (json/yaml/etc).

    This would generally indicate a bug with the remote api or a mismatch between the expected and actual
    response formats.
    """
    pass

class InvalidEntity(Exception):
    """Raised if an Entity cannot be parsed from a raw api response.

    Generally, this should only happen if an Entity's schema is incorrectly defined or a remote api contains a bug.
    """
    pass

class Entity(Mapping):
    """Represents a single api entity.

    The purpose of an Entity implementation is to act as a data container that can be freely passed
    between components that leverage api functionality. Generally speaking, all communication between
    disparate apis should be handled in terms of their corresponding Entity implementations.

    Most of the functionality of this class is derived from the @p schema abstractproperty.
    If the underlying schema is a dictionary, the Entity subclass will automatically be given a corresponding attribute for each key in the dictionary.
    This allows Entity subclasses to be defined in terms of typed schemas but interacted with as if they were normal Python objects.

    This can be demonstrated by the following example (using JsonEntity as a concrete example, but any serialization method would function similarly):
    @code
    from pycamunda.entity import JsonEntity
    from voluptuous import Schema, Required, Optional

    class ExampleEntity(JsonEntity):
      @property
      def schema(self):
        return Schema({
          Required('example_id': Number),
          Required('name': Text),
          Optional('email': Text)
        })

    failing_1 = ExampleEntity('this is not json') # Raises MalformedEntity because the string cannot be decoded
    failing_2 = ExampleEntity({'example_id': 'not a number', 'name': 'anything'}) # Raises InvalidEntity because "example_id" is supposed to be a number, but is a string
    entity = ExampleEntity({'example_id': 123, 'name': 'john'})
    print type(entity.email) # Prints <type 'NoneType'> because the optional attribute was not set
    print entity.name # Prints 'john'
    @endcode
    """
    def __init__(self, raw): #pylint: disable=super-init-not-called
        """@param raw The raw string representing the Entity as it is returned from the remote api, or a dictionary if the Entity is nested.
        @throws InvalidEntity if the Entity's defined schema is violated.
        @throws MalformedEntity if @p raw is a string and could not be decoded by @p decoder.
        """
        self.raw = raw
        try:
            if not isinstance(raw, dict):
                raw = self.decoder(raw) #pylint: disable=not-callable,too-many-function-args
            self.decoded = self.schema(raw) #pylint: disable=not-callable,too-many-function-args
        except voluptuous.Error:
            log.exception('Api response failed Entity schema validation: %s', self.raw)
            exc_info = sys.exc_info()
            raise InvalidEntity, exc_info[1], exc_info[2]
        except Exception:
            log.exception('Failed to parse api response using decoder %s: %s', self.decoder.__name__, self.raw)
            exc_info = sys.exc_info()
            raise MalformedEntity, exc_info[1], exc_info[2]
        if isinstance(self.schema.schema, dict):
            for key in self.schema.schema.iterkeys():
                setattr(self, str(key), self.decoded.get(key))

    @abstractproperty
    def decoder(self):
        """Returns the callable decoder that should be used to translate raw string data into the underlying entity dictionary.

        @returns A unary function that accepts a string and returns a dictionary.
        """
        pass

    @abstractproperty
    def schema(self):
        """Returns the voluptuous.Schema instance associated with the Entity implementation.

        This schema is used to validate the Entity's contents before it is parsed into its typed variant.

        @returns A voluptuous.Schema instance.
        @see https://pypi.python.org/pypi/voluptuous
        """
        pass

    @classmethod
    def build(cls, **kwargs):
        """Constructs an Entity from provided keyword arguments.

        Each keyword will be treated as a key in the underlying representation mapped to its corresponding value.
        Schema validation will be applied; specifying invalid keys or values will result in calls to this method failing.

        @param cls
        @param kwargs Keyword arguments to construct the entity.
        @returns An Entity instance.
        @throws InvalidEntity if @p kwargs does not properGetDeploymentResourcesly specify an instance of the Entity subclass.
        """
        return cls(kwargs) #pylint: disable=no-value-for-parameter

    def __getitem__(self, key):
        return self.decoded[key]

    def __iter__(self):
        return iter(self.decoded)

    def __len__(self):
        return len(self.decoded)

    def __str__(self):
        return str(self.decoded)

    def __repr__(self):
        return repr(self.decoded)

class JsonEntity(Entity): #pylint: disable=abstract-method
    """An abstract Entity implementation for entities that will be loaded from raw json.

    This is mainly a convenience to allow nested Entity implementations to be used easily with
    voluptuous.Coerce.
    """
    @property
    def decoder(self):
        return json.loads

class RequestsInput(object):
    """An interface for data types that can be used as payloads in remote HTTP requests.
    """
    __metaclass__ = ABCMeta
    @abstractmethod
    def to_requests(self):
        """Formats the data so that it is compatible with an outgoing HTTP request.

        @returns A dictionary containing keyword arguments.
        @see requests.request.
        """
        pass

class JsonInputEntity(JsonEntity, RequestsInput): #pylint: disable=abstract-method,too-many-ancestors
    """An abstract Entity implementation for entities that can be sent to the Camunda REST api.
    """
    def __init__(self, **kwargs):
        super(JsonInputEntity, self).__init__(kwargs)

    def to_requests(self):
        return {'data': self}

class FormOption(object):
    """Models possible options for multipart form data options.
    """
    def __init__(self, content_type='text/plain', headers=None):
        self.content_type = content_type
        self.headers = headers or {}

class MultipartFormInput(RequestsInput):
    """A RequestsInput implementation for entities that must be sent as multipart forms to the Camunda REST api.
    """
    def __init__(self, files, **kwargs):
        """@param files A dictionary mapping file names to their content.
        @param kwargs Keyword arguments to be forwarded through options_by_name.
        """
        self.files = {name: (None, data, 'application/octet-stream', {}) for name, data in files.iteritems()}
        for name, data in kwargs.iteritems():
            name = name.replace('_', '-')
            try:
                options = self.options_by_name[name]
            except KeyError:
                raise ValueError('Unknown option {}'.format(name))
            self.files[name] = (None, data, options.content_type, options.headers)

    @abstractproperty
    def options_by_name(self):
        """Retrieves the options (content type and headers) for each name supported by the form input.

        @returns A dictionary mapping form names to FormOption instances.
        """
        pass

    def to_requests(self):
        return {'files': self.files}
