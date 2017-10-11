import json
import logging

import boto3

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

APPLICABLE_RESOURCES = ["AWS::S3::Bucket"]


def evaluate_compliance(configuration_item):
    logger.info('Configuration item: {}'.format(json.dumps(configuration_item, indent=4)))
    if configuration_item["resourceType"] not in APPLICABLE_RESOURCES:
        return "NOT_APPLICABLE"

    raw_policy = configuration_item['supplementaryConfiguration']['BucketPolicy'].get('policyText')
    if raw_policy is not None:
        policy = json.loads(raw_policy)
        logger.info('Bucket policy: {}'.format(json.dumps(policy, indent=4)))
        for i in policy['Statement']:
            try:
                if (not (not (i['Effect'] == 'Deny') or not (
                    i['Condition']['StringNotEquals']['s3:x-amz-server-side-encryption'] == 'aws:kms')) and
                        's3:PutObject' in i['Action']
                ):
                    return "COMPLIANT"
            except:
                pass
    else:
        logger.warn('Empty bucket policy for {}!!'.format(configuration_item['resourceName']))

    return "NON_COMPLIANT"


def lambda_handler(event, context):
    logger.info('Event: {}'.format(json.dumps(event)))

    invoking_event = json.loads(event.get('invokingEvent'))
    configuration_item = invoking_event.get('configurationItem')
    if configuration_item is None:
        logger.warn('Not something I can evaluate.')
        return

    result_token = "No token found."
    if "resultToken" in event:
        result_token = event["resultToken"]

    config = boto3.client("config")
    config.put_evaluations(
        Evaluations=[
            dict(ComplianceResourceType=configuration_item["resourceType"],
                 ComplianceResourceId=configuration_item["resourceId"],
                 ComplianceType=evaluate_compliance(configuration_item),
                 Annotation="Bucket policy enforces object encryption.",
                 OrderingTimestamp=configuration_item["configurationItemCaptureTime"]),
        ],
        ResultToken=result_token
    )
