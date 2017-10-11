import json
import logging

import boto3
import datetime

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def evaluate_compliance(access_key, max_age):
    key_age = datetime.datetime.now() - access_key['CreateDate'].replace(tzinfo=None)
    logger.info('Access key {} is {} days old.'.format(access_key['AccessKeyId'], key_age.days))

    if key_age.days > int(max_age):
        return {
            "compliance_type": "NON_COMPLIANT",
            "key_age": key_age
        }
    else:
        return {
            "compliance_type": "COMPLIANT",
            "key_age": key_age
        }


def lambda_handler(event, context):
    logger.info('Event: {}'.format(json.dumps(event)))

    invoking_event = json.loads(event.get('invokingEvent'))
    rule_parameters = json.loads(event.get('ruleParameters'))

    max_age = rule_parameters['MaxAge']

    iam = boto3.client('iam')
    user_list = iam.list_users()

    access_key_list = []
    for user in user_list['Users']:
        user_access_keys = iam.list_access_keys(UserName=user['UserName'])
        for key_list in user_access_keys['AccessKeyMetadata']:
            access_key_list.append(key_list)

    config = boto3.client("config")
    if len(access_key_list) == 0:
        config.put_evaluations(
            Evaluations=[
                {
                    "ComplianceResourceType":
                        "AWS::IAM::User",
                    "ComplianceResourceId":
                        "ALL USERS",
                    "ComplianceType":
                        "INSUFFICIENT_DATA",
                    "Annotation":
                        "No access keys found in account",
                    "OrderingTimestamp":
                        invoking_event['notificationCreationTime']
                },
            ],
            ResultToken=event["resultToken"]
        )
    else:
        for access_key in access_key_list:
            result = evaluate_compliance(access_key, max_age)
            config.put_evaluations(
                Evaluations={
                    dict(ComplianceResourceType="AWS::IAM::User",
                         ComplianceResourceId="User: {}; AccessKey: {}".format(access_key['UserName'],
                                                                               access_key['AccessKeyId']),
                         ComplianceType=result['compliance_type'],
                         Annotation="Access keys older than {} days must be rotated. This key is {} days old.".format(
                             max_age,
                             result['key_age'].days), OrderingTimestamp=invoking_event['notificationCreationTime']),
                },
                ResultToken=event["resultToken"]
            )
