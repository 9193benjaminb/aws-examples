#!/usr/local/bin/python3
import boto3
client = boto3.client('ec2')

regions =[]
r_count=0
az_count=0
for region in client.describe_regions()["Regions"]:
    regions.append(region['RegionName'])
regions = sorted(regions)
#print(regions)
for region in regions:
    client = boto3.client('ec2', region_name = region)
    r_count += 1
    rn = "%s %s" % (r_count, region)
    print(rn)
    for zone in client.describe_availability_zones()['AvailabilityZones']:
        if zone['State'] == 'available':
            az_count += 1
            az = "\t%s\t%s" % (az_count, zone['ZoneName'])
            print(az)
print("regions: ", r_count )
print("AZ's: ", az_count )