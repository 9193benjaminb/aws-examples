import json
import logging

import boto3

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def evaluate_compliance(account_summary):
    logger.info(account_summary)
    if int(account_summary['SummaryMap']['AccountAccessKeysPresent']) == 0:
        return "COMPLIANT"
    else:
        return "NON_COMPLIANT"


def lambda_handler(event, context):
    logger.info('Event: {}'.format(json.dumps(event)))

    invoking_event = json.loads(event.get('invokingEvent'))
    invoke_time = invoking_event.get('notificationCreationTime')

    result_token = "No token found."
    if "resultToken" in event:
        result_token = event["resultToken"]

    iam = boto3.client('iam')
    account_summary = iam.get_account_summary()

    config = boto3.client("config")
    response = evaluate_compliance(account_summary)
    print response
    config.put_evaluations(
        Evaluations=[
            dict(ComplianceResourceType="AWS::IAM::User", ComplianceResourceId="root", ComplianceType=response,
                 Annotation="Root account must not have access keys present!", OrderingTimestamp=invoke_time),
        ],
        ResultToken=result_token
    )
