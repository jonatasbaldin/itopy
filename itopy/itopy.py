"""
Python library for iTOP API
github.com/jonatasbaldin/itopy
"""

import requests, json

class MyException(Exception):
    """
    Handle custom exceptions
    """
    pass

class Api(object):
    """
    To instanciate an itopy object.
    No parameter needed.
    """

    def __init__(self):
        """
        Just init
        """
        pass

    def connect(self, url, version, auth_user, auth_pwd):
        """
        Connect to iTOP JSON webservice.
        Parameters:
        url: url to iTOPs rest.php page
        version: API version
        auth_user: user to authenticate
        auth_pwd: user password
        """
        self.url = url
        self.version = version
        self.auth_user = auth_user
        self.auth_pwd = auth_pwd
        self.auth = 1

        # Construct a dictionary
        data = {
            'operation': 'core/check_credentials',
            'user': self.auth_user,
            'password': self.auth_pwd
        }

        # Converts dict to str (json object)
        json_data = json.dumps(data)

        # Multiple  exceptions
        schema_exceptions = (requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema)

        # Tries web request
        try:
            req = requests.post(self.url, data={'version': self.version,
                'auth_user': self.auth_user, 'auth_pwd': self.auth_pwd,
                'json_data': json_data})
        except schema_exceptions  as e:
            return 'The http:// is missing or invalid'
        except requests.exceptions.ConnectionError as e:
            return 'The connection to iTOP was refused'

        if req.status_code != 200:
            return 'Could not connect. HTTP code {}'.format(req.status_code)

        # The return is 'bytes', convert to string
        try:
            return_code = json.loads(req.content.decode('utf-8'))['code']
        except ValueError as e:
            return 'Not a valid JSON, maybe the page is returning other data'

        # Authenticate
        if return_code == 0:
            self.auth = 0
            return self.auth
        else:
            try:
                # If not, return custom excpetion with iTOP connection error
                self.auth = 1
                # Raises custom exception
                raise MyException(self.connect_error(return_code))
            except MyException as e:
                # Returns just custom exception message
                return e.args[0]

    def auth(func):
        """
        Decorator to authenticate the functions that must be authenticated
        Parameters:
        func: function to authenticate
        """
        # gets the function and all its parameters
        def inner(self, *args, **kwargs):
            # verify if self.auth is 0 (auththenticated) or not
            if self.auth == 0:
                # if it ts, return the function with normal request
                return func(self, *args, **kwargs)
            else:
                # if not, returns that it is not authenticated
                return self.connect_error(self.auth)
        # returns the inner function
        return inner

    def connect_error(self, error):
        """
        Return connection error, if any.
        """
        error_dict = { 
            0: 'OK - No issue has been encountered',
            1: """UNAUTHORIZED - Missing/wrong credentials or the user does 
                not have enough rights to perform the requested operation""",
            2: "MISSING_VERSION - The parameter 'version' is missing",
            3: "MISSING_JSON - The parameter 'json_data' is missing",
            4: 'INVALID_JSON - The input structure is not valid JSON string',
            5: "MISSING_AUTH_USER - The parameter 'auth_user' is missing",
            6: "MISSING_AUTH_PWD - The parameter 'auth_pwd' is missing",
            10: """UNSUPPORTED_VERSION - No operation is available for 
                the specified version""",
            11: """UNKNOWN_OPERATION - The requested operation is not valid   
                for the specelified version""",
            12: """UNSAFE - The requested operation cannot be performe because
                it can cause data (integrity) loss""",
            100: """INTERNAL_ERROR - The operation could not be performed, 
                see the message for troubleshooting""",
        }
    
        if error_dict.get(error):
            return error_dict[error]
        else:
            return 'UNKNOW_ERROR - Not specified by ITOP'
    @auth
    def req(self, data, obj_class):
        """
        Gereral request to iTOP API.
        Handles requests for all functions.
        Parameters:
        data: JSON structure data, in dict
        ojb_class: iTOP's device class from datamodel
        """
        json_data = json.dumps(data)
        #json_data = jsonpickle.encode(data)

        # Multiple  exceptions
        schema_exceptions = (requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema)

        # Tries web request
        try:
            req = requests.post(self.url, data={'version': self.version,
                'auth_user': self.auth_user, 'auth_pwd': self.auth_pwd,
                'json_data': json_data})
        except schema_exceptions  as e:
            return 'The http:// is missing or invalid'
        except requests.exceptions.ConnectionError as e:
            return 'The connection to iTOP was refused'

        try:
            json_return = json.loads(req.content.decode('utf-8'))
        except ValueError as e:
            return 'Not a valid JSON, maybe the page is returning other data'

        # The return is 'bytes', convert to string
        return_code = json_return['code']

        # Default return_list 
        return_list = {
                        'code': json_return['code'],
                        'message': json_return['message'],
                      }

        # if there's no error, returns +objects and +item_key
        if return_code == 0:
            # create a dict key for the items
            # useful for Get
            item_key = None
            temp_dict = (json_return['objects'])
            item_key = list()
            if temp_dict is not None:
                for key in json_return['objects']:
                    item_key.append(json_return['objects'][key]['key'])
                
                # old comprehension..
                #item_key.append(int([objects[p]['key'] for p in objects][0]))

            # adds objects and item_key do dict
            return_list['objects'] = json_return['objects']
            return_list['item_key'] = item_key

        return return_list

    def check_class(self, obj_class):
        """
        Used to return the right field to be searched when an object
        is being added, to check if it exists.
        Created because some objects no 'name' field, so one correct must
        be specified.
        The default return is name, which is default for a lot of objects,
        if it should not be, it's gonna return an iTOP's error
        Parameters:
        obj_class: iTOP's device class from datamodel
        """
        obj_dict = {
            'VLAN': 'vlan_tag',
            'IPv4Address': 'ip',
            'lnkConnectableCIToNetworkDevice': 'dontcheck',
            'IPv4Range':'range'
        }
        
        if obj_dict.get(obj_class):
            return obj_dict[obj_class]
        else:
            return 'name'

    @auth
    def get(self, obj_class, key, output_fields='*'):
        """
        Handles the core/get operation in iTOP.
        Parameters:
        ojb_class: iTOP's device class from datamodel
        key: search filter in iTOP's datamodel
        output_fields: fields to get from iTOP's response, defaults is name
        """

        data = {
            'operation': 'core/get',
            'comment': 'Get' + obj_class,
            'class': obj_class,
            'key': key,
            'output_fields': output_fields
        }

        request = self.req(data, obj_class)
        return request

    @auth
    def delete(self, obj_class, simulate=False, key=None, **kwargs):
        """
        Handles the core/delete operation in iTOP.
        Parameters:
        ojb_class: iTOP's device class from datamodel
        simulate: False by default
        key: search key; can be OQL filter or object id. Warning : will override any kwargs
        **kwargs: any field from the datamodel to identify the object
        """

        data = {
            'operation': 'core/delete',
            'comment': self.auth_user + ' (api)',
            'simulate': simulate,
            'class': obj_class,
            'key': {
            }
        }

        for k, value in kwargs.items():
            if value:
                data['key'][k] = value
            if not value:
                return 'Parameter not valid!'

        if(key != None):
            data['key']=key
        request = self.req(data, obj_class)
        return request

    @auth
    def create(self, obj_class, output_fields='*', **kwargs):
        """
        Handles the core/create operation in iTOP.
        Parameters:
        obj_class: iTOP's device class from datamodel
        output_fields: fields to get from iTOP's response
        **kwargs: any field to add in the object from the datamodel, note that
            some fields, like brand_name is not added without its id, brand_id,
            it is recommended to use just brand_id, in that case
        """

        # verifies if object exists
        # filter to get the object
        # unless dontcheck, those objects may have duplicates
        obj_field = self.check_class(obj_class)
        if obj_field == 'dontcheck':
            obj = dict()
            obj['message'] = 'Found: 0'
            obj['code'] = 0
        else:
            get_filter = "SELECT {} WHERE {} = '{}'".format(obj_class, obj_field, kwargs[obj_field])
            # actual request
            obj = self.get(obj_class, get_filter)

        # if found 0 objects, and the return code is ok
        if obj['message'] == 'Found: 0' and obj['code'] == 0:
            data = {
                'operation': 'core/create',
                'comment': self.auth_user + ' (api)',
                'class': obj_class,
                'output_fields': output_fields,
                'fields': {
                }
            }

            # when creating DocumentFile, file parameter is specified
            # it's a reserved word, so in the request we use _file
            # and translate here to a key 'file'
            if '_file' in kwargs:
                for item in kwargs['_file']:
                    kwargs['file'] = item
                del kwargs['_file']

            # do not allow empty values in parameters
            for key, value in kwargs.items():
                if value:
                    data['fields'][key] = value
                if not value:
                    return 'Parameter not valid'

            request = self.req(data, obj_class)
            return request

        # if not 'Found: 0', but found something, obj exists
        elif 'Found' in obj['message']:
            return {
                'message': 'Object exists',
                'code': 0
            }
        else:
            # if found is not present in string, probably error
            return obj

    @auth
    def update(self, obj_class, key, key_value, output_fields='*', **kwargs):
        """
        Handles the core/update operation in iTOP.
        TODO: Until now just handles objects that have 'name' field
        Parameters:
        obj_class: iTOP's device class from datamodel
        output_fields: fields to get from iTOP's response
        key: field to identify the the unique object 
        key_value: value to the above field
        **kwargs: any field to update the object from the datamodel, note that
            some fields, like brand_name is not added without its id, brand_id,
            it is recommended to use just brand_id, in that case
        """



        data = {
            'operation': 'core/update',
            'comment': self.auth_user + ' (api)',
            'class': obj_class,
            'output_fields': output_fields,
            'fields': {
            },
            'key': {
                key: key_value
             }
        }

        if key == 'key':
            data['key'] = key_value

        # do not allow empty values in parameters
        for kkey, kvalue in kwargs.items():
            if kvalue:
                data['fields'][kkey] = kvalue
            if not kvalue:
                return 'Parameter not valid'

        request = self.req(data, obj_class)
        return request
