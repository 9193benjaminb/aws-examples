import json
import logging

import boto3

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def evaluate_compliance(account_summary):
    logger.info(account_summary)
    if int(account_summary['SummaryMap']['Users']) == 0:
        return "COMPLIANT"
    else:
        return "NON_COMPLIANT"


def lambda_handler(event, context):
    logger.info('Event: {}'.format(json.dumps(event)))

    invoking_event = json.loads(event.get('invokingEvent'))
    invoke_time = invoking_event.get('notificationCreationTime')

    iam = boto3.client('iam')
    account_summary = iam.get_account_summary()
    compliance_type = evaluate_compliance(account_summary)

    config = boto3.client("config")
    config.put_evaluations(
        Evaluations=[
            dict(ComplianceResourceType="AWS::IAM::User", ComplianceResourceId="User Principals",
                 ComplianceType=compliance_type, Annotation="User principals are not allowed in AWS accounts",
                 OrderingTimestamp=invoke_time),
        ],
        ResultToken=event["resultToken"]
    )
