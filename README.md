webservice
=====

This library lets you model web services as Python classes. It comes with two types of classes:

* `WebService`: used to encapsulate a web service

* `WebServiceBatcher`: used to group web service requests when you want to iterate over individual elements but the web service accepts groups of elements.

Dependencies
----

This library depends on `requests` and `lxml`.


Defining a web service
-----

The concept behind this architecture comes from Django. A class represents a data source--just in this case the data source is either a JSON- or XML-returning web service. There are two super-classes: `webservice.JSONWebService` and `webservice.XMLWebService`.

The following keys can exist for the class:

* `PARAMS`: a list of objects inheriting from `webservice.BaseParam`. (See below.)

* `BASE_URL`: the base for the web service.

* `WALK_KEYS`: a list. If defined, when the web service response is converted into a Python structure these keys will be `walked`. For example if the stuff you want is all in `response['result']['goodstuff']`, if you specify `('result', 'goodstuff',)` then the objects you receive will only be what's under that part of the response.

Defining parameters
-----

Right now there are two types of parameters:

* `webservice.Param`: needs `param_name` specified. Optional arguments are:

    * `required`: Is this parameter required on every request?

    * `multi`: Can this parameter be specified more than once?

    * `multi_delimiter`: If specified, then the key will be specified **ONCE** and the values will be joined on this parameter. For example, `key=val1,val2,val3,val4`. If NOT specified, the key/value pair will be repeated for each value (e.g. `key=val1&key=val2&key=val3&key=val4`.

* `webservice.ConstantParam`: needs `param_name` and `value` specified. This paramater will then always be sent. Good for program identification.


Web service methods
-----

* `url()`: returns the URL that would be called. Good for testing.

* `get()`: calls the URL and gets a response. Note this calls `sleep()` to sleep before the fetch--currently specified as 5 seconds. This is to be a good netizen.

XML objects are created via `lxml`'s `objectify.fromstring`. JSON objects are created by `json`'s `json.loads`.

Usage
-----

In this example, you encapsulate an XML web service that takes several parameters. You specify which parameters are required and which ones are multi-valued. You can also specify a 'constant parameter' that never changes across web service requests.

    import webservice

    class ExampleWebService(webservice.XMLWebService):
        PARAMS = (
            webservice.Param(param_name='opt-param'),
            webservice.Param(param_name='required-multi-param',
                             required=True,
                             multi=True,
                             ),
            webservice.Param(param_name=opt-param'),
            webservice.Param(param_name='opt-multi-param',
                             multi=True,
                             ),
            webservice.Param(param_name='opt-param'),
            webservice.ConstantParam(param_name='program-name',
                                             value='my-cool-program'),
			
            )
    
        BASE_URL = "http://api.example.com/api/example"
        WALK_KEYS = ('result',)

This class is then used as so:

    ews = ExampleWebService('required_multi_param': [1, 2, 3])
	objs = ews.get()
	for obj in objs:
        print "Got object %s" % obj

or whatever.

Here's an example of the batcher:

    ews = ExampleWebService()
	batcher = webservice.WebServiceBatcher(
	    iterate_over=(('required_multi_param', [range(10000)])),
		batch_size=5,
		webservice=ews,
		)
	for ws in batcher.yield_objs():
	    for obj in ws.get().objs():
		    print "Got object %s" % obj


Copyright and warranty
----

No warranty is expressed or implied. Library released under the MIT license:

Copyright (c) 2013, John Borwick

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
