"""@ingroup pycamunda pycamunda
@file
Implementation of the HTTP/S connector to the Camunda REST api.
"""
import logging
from abc import ABCMeta, abstractproperty
from collections import namedtuple

from enum import Enum
import requests

from .system import System

log = logging.getLogger(__name__)

class AccessCredentials(object):
    """Handles resolution of arbitrary access credentials.

    Credentials can be supplied to pycamunda using a few different sources that will be checked in order:
    <ol>
    <li>Directly supplying credentials from code (not recommended)</li>
    <li>Retrieving credentials from environment variables (KEY=credentials)</li>
    <li>Retrieving credentials from a file on the underlying host (a pycamunda file in the current working directory containing the credentials)</li>
    </ol>
    """
    def __init__(self, credentials=None, system=None):
        self.system = system or System()
        if credentials is None:
            credentials = self.find_credentials()
            if credentials is not None:
                try:
                    credentials = self.process_credentials(credentials)
                except ValueError:
                    log.exception('Failed to process credentials: %s', credentials)
                    credentials = None
        self.credentials = credentials

    @abstractproperty
    def key(self):
        """Returns the unique key used to identify the credential type.

        This key is used for both the environment variable and file name for credential retrieval.
        The environment variable will use key.upper() while the file name will use key.lower().

        @returns A string.
        """
        pass

    def process_credentials(self, credentials): #pylint: disable=no-self-use
        """A hook for processing the raw credential string found from the underlying system.

        This is useful for situations in which credential information is not encoded as a simple string.
        For example, a username/password combination could be encoded on the system as 'username:password'.
        In this case, process_credentials would unpack the string into a (username, password) tuple by splitting on ':'.

        The default behavior is raw string passthrough.

        @throws ValueError if @p credentials cannot be properly processed.
        """
        return credentials

    def find_credentials(self):
        """Attempts to locate credentials from the current running environment.

        This method should never raise.

        @returns A string, or None if no credentials could be found.
        """
        environment_value = self.system.get_environment_variable(self.key.upper())
        if environment_value is not None:
            log.debug('Environment variable set, reading credentials')
            return environment_value.strip()

        file_name = self.key.lower()
        if self.system.is_file(file_name):
            log.debug('Credentials file exists, reading credentials')
            try:
                return self.system.read_file(file_name).strip()
            except (EnvironmentError, ValueError):
                log.warning('Credentials file value malformed, skipping')

        log.warning('No credentials found')
        return None

UsernamePasswordPair = namedtuple('UsernamePasswordPair', ['username', 'password'])

class UsernamePasswordAccessCredentials(AccessCredentials):
    """An AccessCredentials implementation for apis that can be authenticated against with a username/password pair.

    Credentials retrieved with UsernamePasswordAccessCredentials should be stored in text as 'username:password'.
    """
    def __init__(self, system=None, user=None, password=None):
        """@param system An pycamunda.system.System instance.
        @param user A username (not recommended).
        @param password A password (not recommended).
        """
        if user is None != password is None:
            raise ValueError('user and password must be supplied together or not at all')
        if user is not None:
            credentials = '{}:{}'.format(user, password)
        else:
            credentials = None
        super(UsernamePasswordAccessCredentials, self).__init__(credentials=credentials, system=system)

    @property
    def key(self):
        return 'pycamunda'

    def process_credentials(self, credentials):
        username, password = credentials.split(':', 1)
        return UsernamePasswordPair(username.strip(), password.strip())

    @property
    def username(self):
        """Returns the username component of the credentials.

        @returns A string, or None if credentials could not be loaded.
        """
        if self.credentials is None:
            return None
        return self.credentials.username

    @property
    def password(self):
        """Returns the password component of the credentials.

        @returns A string, or None if credentials could not be loaded.
        """
        if self.credentials is None:
            return None
        return self.credentials.password

class HttpMethod(object):
    """An enum class containing all valid HTTP methods.
    """
    Get = 'GET'
    Post = 'POST'
    Put = 'PUT'
    Delete = 'DELETE'
    Head = 'HEAD'
    Options = 'OPTIONS'
    Connect = 'CONNECT'

class Endpoint(object):
    """Models an HTTP api endpoint.

    Endpoints generally consist of a few common features:
    <ul>
    <li>The HTTP method for the operation</li>
    <li>The URI for the endpoint</li>
    <li>Optionally, headers that are expected for the operation</li>
    <li>Optionally, an expected return value</li>
    </ul>
    """
    __metaclass__ = ABCMeta
    def __init__(self, engine_name=None):
        """@param engine_name The name of the process engine that should be used for the api request.
        If this parameter is set, the endpoint will attempt to communicate directly with the named process engine
        rather than the default.
        TODO: Not all endpoints can be used with a named process engine; would probably be good to model this in the
        client somehow.
        """
        self.engine_name = engine_name
        self.parameters = None

    @abstractproperty
    def method(self):
        """Returns the HTTP method to use for communication with the endpoint.

        @returns An HttpMethod value.
        """
        pass

    @abstractproperty
    def uri(self):
        """Returns the URI to use for communication with the endpoint.
        This should always begin with a leading slash.

        @returns A string.
        """
        pass

    @property
    def engine_uri(self):
        """Returns the URI to use for communication with the endpoint normalized for named engine use.
        If there is no named engine, the default process engine will be used instead.

        @returns A string.
        """
        if self.engine_name is not None:
            return '/engine/{}{}'.format(self.engine_name, self.uri)
        return self.uri

    @property
    def headers(self): #pylint: disable=no-self-use
        """Returns the headers to use for communication with the endpoint.

        @returns A dictionary, or None.
        """
        return None

    @property
    def timeout(self): #pylint: disable=no-self-use
        """Returns the timeout (in seconds) that should be used for communication with the endpoint.

        @returns A float.
        """
        return 10.0

    @property
    def parameters_type(self): #pylint: disable=no-self-use
        """Returns the required type of the query parameters object required for communication with the endpoint.

        @returns A JsonInputEntity subclass, or None.
        """
        return None

    def with_parameters(self, **kwargs):
        """Adds parameters to the endpoint request.

        This will construct an instance of Endpoint.parameters_type and associate it with the endpoint instance.

        @returns An Entity instance.
        @throws ValueError if Endpoint.parameters_type returns None.
        @throws voluptuous.Invalid if @p kwargs are not valid in the context of Endpoint.parameters_type.
        """
        if self.parameters_type is None:
            raise ValueError('Cannot add parameters when parameters_type is None')
        self.parameters = self.parameters_type(**kwargs) #pylint: disable=not-callable
        return self

    @property
    def parameters_required(self): #pylint: disable=no-self-use
        """Whether or not parameters are required for the endpoint to be successfully used.

        @returns A boolean
        """
        return False

    @property
    def params(self): #pylint: disable=no-self-use
        """Returns query string parameters to use for communication with the endpoint.

        @returns A dictionary, or None.
        """
        if self.parameters is None:
            if self.parameters_required:
                raise ValueError('Parameters required but not suppled for endpoint')
            return None

        params = {}
        for key, value in self.parameters.iteritems():
            if isinstance(value, Enum):
                params[key] = value.value
            else:
                params[key] = value
        return params

    @property
    def return_type(self): #pylint: disable=no-self-use
        """Returns the expected type of data returned by communication with the endpoint.

        @returns A subtype of pycamunda.entity.Entity, or None if any return value should be discarded.
        """
        return None

class DeleteEndpoint(Endpoint): #pylint: disable=abstract-method
    """An abstract Endpoint implementation for operations that use the HTTP DELETE method.
    """
    @property
    def method(self):
        return HttpMethod.Delete

class GetEndpoint(Endpoint): #pylint: disable=abstract-method
    """An abstract Endpoint implementation for operations that use the HTTP GET method.
    """
    @property
    def method(self):
        return HttpMethod.Get

class OptionsEndpoint(Endpoint): #pylint: disable=abstract-method
    """An abstract Endpoint implementation for operations that use the HTTP OPTIONS method.
    """
    @property
    def method(self):
        return HttpMethod.Options

class PostEndpoint(Endpoint): #pylint: disable=abstract-method
    """An abstract Endpoint implementation for operations that use the HTTP POST method.
    """
    @property
    def method(self):
        return HttpMethod.Post

class PutEndpoint(Endpoint): #pylint: disable=abstract-method
    """An abstract Endpoint implementation for operations that use the HTTP PUT method.
    """
    @property
    def method(self):
        return HttpMethod.Put

class CamundaException(Exception):
    """The base class for all exceptions explicitly raised by pycamunda.
    """
    def __init__(self, response):
        response_dict = response.json()
        super(CamundaException, self).__init__(response_dict['message'])
        self.api_type = response_dict['type']

class BadRequest(CamundaException):
    """Raised if an API request is somehow malformed.
    """
    pass

class ResourceNotFound(CamundaException):
    """Raised if an API operation is attempted with a resource id that could not be found by the Camunda server.
    """
    pass

class Camunda(object):
    """Handles connectivity to the Camunda REST api.
    """
    def __init__(self, base_url, access_credentials=None):
        self.base_url = base_url + '/engine-rest'
        self.headers = {'Content-Type': 'application/json'}
        self.cache = {}
        if access_credentials is not None:
            self.auth = requests.auth.HTTPBasicAuth(access_credentials.username, access_credentials.password)
        else:
            self.auth = None

    def communicate_with(self, endpoint, payload=None, cache=False):
        """Sends an HTTP request to the specified endpoint.

        @param endpoint An Endpoint subclass instance.
        @param payload Data to be sent along with the request.
        @param cache Whether the response should be cached.
        If not set to True, the internal cache will never be used.
        If set to True, the first request for an endpoint will contact the remote while subsequent requests return the cached response.
        @returns An instance of @p endpoint.return_type.
        @see http://docs.python-requests.org/en/master/api/#requests.request
        """
        if cache and endpoint in self.cache:
            return self.cache[endpoint]
        url = self.base_url + endpoint.uri
        log.debug('Sending request to Camunda endpoint %s', url)
        response = requests.request(endpoint.method, url, auth=self.auth,
                                    headers=endpoint.headers, timeout=endpoint.timeout, params=endpoint.params,
                                    data=payload)
        # TODO: Deal with standard api exceptions
        if response.status_code == 400:
            raise BadRequest(response)
        if response.status_code == 404:
            raise ResourceNotFound(response)

        if endpoint.return_type is None:
            return None

        cleaned_response = response.text.replace(')]}\'\n', '', 1)
        response = endpoint.return_type(cleaned_response)
        if cache:
            self.cache[endpoint] = response
        return response
