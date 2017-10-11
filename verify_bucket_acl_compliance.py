import json
import logging

import boto3
import datetime

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def evaluate_compliance(configuration_item):
    acl = json.loads(configuration_item['supplementaryConfiguration']['AccessControlList'])

    owner = acl['owner']['displayName']
    grant_list = acl.get('grantList')

    if grant_list is None:
        return "NOT_APPLICABLE"

    if len(acl['grantList']) != 1:
        return "NON_COMPLIANT"
    elif (grant_list[0]['grantee']['displayName'] != owner) or (grant_list[0]['permission'] != "FullControl"):
        return "NON_COMPLIANT"
    else:
        return "COMPLIANT"


def lambda_handler(event, context):
    logger.info('Event: {}'.format(json.dumps(event)))

    # Deserialize invoking event
    invoking_event = json.loads(event.get('invokingEvent'))
    configuration_item = invoking_event.get('configurationItem')

    if event['eventLeftScope']:
        compliance_type = "NOT_APPLICABLE"
    else:
        compliance_type = evaluate_compliance(configuration_item)

    config = boto3.client("config")
    config.put_evaluations(
        Evaluations=[
            dict(ComplianceResourceType=configuration_item["resourceType"],
                 ComplianceResourceId=configuration_item["resourceId"], ComplianceType=compliance_type,
                 Annotation="ACL must be set to owner full control only.", OrderingTimestamp=datetime.datetime.now()),
        ],
        ResultToken=event["resultToken"]
    )
