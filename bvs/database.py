from redis import StrictRedis


from os import environ as env

if 'VCAP_SERVICES' in env:
    vcap_services = json.loads(env['VCAP_SERVICES'])
    credentials = vcap_services['redis-2.6'][0]['credentials']
    host = credentials['host']
    port = credentials['port']
    password = credentials['password']
else:
    host = 'localhost'
    port = 6379
    password = None


db = StrictRedis(host=host, port=port, password=password, db=0)
