# Python Wrapper for [Nifty Cloud Mobile Backend](http://mb.cloud.nifty.com/)

This module is a python wrapper for Nifty Cloud Mobile Backend.  
Easy request for Nifty Cloud Mobile Backend RESTful API.

# enviroment

Python 2.7.7 and 3.4.1

# installation

```sh
pip install py_nifty_cloud
```

uploaded to [py_nifty_cloud: Python Package Index](https://pypi.python.org/pypi/py_nifty_cloud)

# how to use

## preparation

make a yaml file (e.g. `~/.nifty_cloud.yml`) contains APPLICATION_KEY and CLIENT_KEY of Nifty

```yaml
APPLICATION_KEY: 'your application key'
CLIENT_KEY: 'your client key'
```

## simple usage

```py
# import 
from py_nifty_cloud.nifty_cloud_request import NiftyCloudRequest

# instanciate with yaml file contains APPLICATION KEY and CLIENT KEY 
ncr = NiftyCloudRequest('~/.nifty_cloud.yml')
path = '/classes/your_class'
query = {'where' : {'key': 'value'}}
method = 'GET'

# standard way to request 
# get recodes which matches a query from path, with GET or POST or PUT http method
response = ncr.request(path=path, query=query, method=method)
type(response)
# >>> requests.models.Response

# show status code 
print(response.status_code)
# show response as json format
print(response.json())

# get a recode from your_class specified by object_id
object_id = 'object_id'
response = ncr.get(
  path='{path}/{object_id}'.format(path=path, object_id=object_id), 
  query={}
)

# post a new recode
values = {'key': 'value'}
response = ncr.get(path=path, query=values)
```


# License

[MIT License](http://petitviolet.mit-license.org/)
