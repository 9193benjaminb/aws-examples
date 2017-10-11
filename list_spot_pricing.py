import boto.ec2
import os

_access_key = os.getenv('AWS_ACCESS_KEY')
_secret_key = os.getenv("AWS_SECRET_KEY")

_connection = boto.ec2.connection.EC2Connection(_access_key, _secret_key)

_results = _connection.get_spot_price_history(instance_type='cg1.4xlarge', product_description='Linux/UNIX')

for result in _results:
    print '%s,%s' % (result.timestamp, result.price)
