import boto.ec2
import os

class _compliance_status:
    compliant = "COMPLIANT"
    non_compliant = "NON-COMPLIANT"
    not_applicable = "NOT_APPLICABLE"

# Variables
_environment_class = ('prod','pre-prod','uat','training','sit')

_access_key = os.getenv('AWS_ACCESS_KEY')
_secret_key = os.getenv('AWS_SECRET_KEY')

_connection = boto.ec2.connection.EC2Connection(_access_key, _secret_key)
_reservations = _connection.get_all_instances()


for _reservation in _reservations:
    for _instance in _reservation.instances:
        print 'instance id = %s'% (_instance.id)
        for _tag in _instance.tags:
            _tag_name = str(_tag)
            if _tag_name == 'environmentclass':
                print '%s %s'% (_tag_name, _instance.tags[_tag])
                if _instance.tags[_tag] not in _environment_class:
                    print 'The %s tag is: %s'%(_tag_name,_compliance_status.non_compliant)
                else:
                    print 'The %s tag is: %s'%(_tag_name,_compliance_status.compliant)
            elif _tag_name == 'environment':
                print '%s %s'% (_tag_name, _instance.tags[_tag])
                if _instance.tags[_tag] not in _environment_class:
                    print 'The %s tag is: %s'%(_tag_name, _compliance_status.non_compliant)
                else:
                    print 'The %s tag is: %s'%(_tag_name,_compliance_status.compliant)
            elif _tag_name == 'application':
                print '%s %s'% (_tag_name, _instance.tags[_tag])
                if _instance.tags[_tag] != "":
                    print 'The %s tag is: %s'%(_tag_name, _compliance_status.compliant)
                else:
                    print 'The %s tag is: %s'%(_tag_name, _compliance_status.non_compliant)
            else:
                print 'The %s tag is: %s'%(_tag_name, _compliance_status.not_applicable)

