import time
import urllib
import json
import copy
import logging

import requests
from lxml import objectify


logger = logging.getLogger(__name__)


class WebService(object):
    # NEED TO BE DEFINED:

    # Ordered list of parameters
    PARAMS = None

    # URL from which query is built:
    BASE_URL = None

    # any keys to run through in the response:
    WALK_KEYS = None

    def __init__(self, **kwargs):
        self.fields = {}
        for (k, v) in kwargs.iteritems():
            if self.has_param(k):
                self.fields[k] = v
            else:
                raise "Do not know about param %s" % k

    def set_field(self, k, v):
        self.fields[k] = v

    def has_param(self, param_name):
        return param_name in [x.param_name for x in self.PARAMS]

    def query_string(self):
        """
        Construct the query string based on self.PARAMS
        """
        # list of tuples:
        param_kv = []
        for param in self.PARAMS:
            # what was stored in self.fields ?
            param_val = self.fields.get(param.param_name, None)
            # now ask the parameter to render that as a list
            qs_elts = param.qs_elts(param_val)
            if qs_elts is not None:
                param_kv.extend(qs_elts)

        if param_kv is None:
            return
        else:
            return '&'.join(["%s=%s" % (k, urllib.quote_plus(str(v)))
                             for (k, v) in param_kv])

    def url(self):
        """
        URL to be used for the query
        """
        query_string = self.query_string()
        if query_string:
            return self.BASE_URL + '?' + query_string
        else:
            return self.BASE_URL

    def sleep(self):
        """
        Sleep a little so I don't overwhelm the service.
        """
        # TODO make this configurable
        time.sleep(5)

    def get(self):
        self.sleep()
        query_url = self.url()
        logger.debug("Going to get() %s" % query_url)
        resp = requests.get(query_url)
        return self.process_response(resp.text)

    def process_response(self, text):
        return_struct = self.text_to_struct(text)

        if self.WALK_KEYS is not None:
            for key in self.WALK_KEYS:
                return_struct = return_struct[key]
        return return_struct


class JSONWebService(WebService):
    def text_to_struct(self, resp):
        
        logger.debug("About to convert to struct:\n%s" % resp)
        return json.loads(resp)


class XMLWebService(WebService):
    def text_to_struct(self, resp):
        return objectfy.fromstring(resp)


class BaseParam(object):
    def __init__(self, param_name, *args, **kwargs):
        self.param_name = param_name

    def qs_elts(self, param_val):
        """
        Generate a list of [k, v]
        """
        return [[self.param_name, param_val],]


class Param(BaseParam):
    """
    required

    multi: should a list be passed?

    multi_delimiter: if set, list will be separated by this.
    otherwise, multiple k/v's will be passed (e.g. k=1&k=2)
    """
    def __init__(self, param_name,
                 required=False,
                 multi=False,
                 multi_delimiter=None,
                 *args, **kwargs):
        super(Param, self).__init__(param_name, *args, **kwargs)
        self.required = required
        self.multi = multi
        self.multi_delimiter = multi_delimiter

    def qs_elts(self, param_val):
        if param_val is None:
            if self.required:
                raise Exception("Required parameter %s not set" % self.param_name)
            else:
                return

        if self.multi:
            if self.multi_delimiter:
                return [[self.param_name,
                         self.multi_delimiter.join([str(v)
                                                    for v in param_val])]
                                                    ,]
            else:
                return [[self.param_name, val_elt]
                        for val_elt in param_val]
        else:
            return super(Param, self).qs_elts(param_val)


class ConstantParam(BaseParam):
    def __init__(self, param_name, value, *args, **kwargs):
        super(ConstantParam, self).__init__(param_name, *args, **kwargs)
        self.value = value

    def qs_elts(self, param_val):
        return [[self.param_name, self.value],]


class WebServiceBatcher(object):
    def __init__(self, iterate_over, batch_size,
                 webservice):
        """
        iterate_over = list of k/v where the value is an iterator.
        Currently only supports ONE k/v pair.

        iterate_over = ((k, v),)
        """
        if len(iterate_over) != 1:
            raise "not implemented: right now iterate_over only supports 1 elt"
        self.iterate_over = iterate_over
        self.batch_size = batch_size
        self.webservice = webservice


    def yield_objs(self):
        (iter_key, iter_val) = self.iterate_over[0]
        for batch_index in range(0, len(iter_val), self.batch_size):
            batch_webservice = copy.deepcopy(self.webservice)
            batch_values = iter_val[batch_index:batch_index + self.batch_size]
            batch_webservice.set_field(iter_key, batch_values)
            yield batch_webservice
