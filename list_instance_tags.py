import boto.ec2
import os

_access_key = os.getenv('AWS_ACCESS_KEY')
_secret_key = os.getenv("AWS_SECRET_KEY")

_connection = boto.ec2.connection.EC2Connection(_access_key, _secret_key)
_reservations = _connection.get_all_instances()


for _reservation in _reservations:
    for _instance in _reservation.instances:
        if 'environmentclass' in _instance.tags:
            print "Tagged Instance\n=============== \nInstanceID: %s \nInstanceState: %s \nEnvironmentClass: %s \nEnvironment: %s \nApplication: %s" % ( _instance.id, _instance.state, _instance.tags['environmentclass'], _instance.tags['environment'],_instance.tags['application'])
        else:
            print "Non-Tagged Instance\n=================== \nInstanceID: %s \nInstance State: %s " % (_instance.id, _instance.state)
