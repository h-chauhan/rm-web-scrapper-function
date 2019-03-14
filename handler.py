import boto3
from botocore.exceptions import ClientError
from robobrowser import RoboBrowser
import hashlib
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
import logging

logger =  logging.getLogger()
logger.setLevel(logging.INFO)
sentry_sdk.init(
    "https://afe5f72242f64022941a47e2e8c947fe@sentry.io/1412608",
    integrations=[AwsLambdaIntegration()]
)


dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
lambda_client = boto3.client('lambda', region_name='ap-south-1')

getParams = lambda type: {
    "loginUrl": "http://tnp.dtu.ac.in/rm_2016-17/intern/intern_login",
    "username_field": "intern_student_username_rollnumber",
    "password_field": "intern_student_password",
    "notifsUrl": "http://tnp.dtu.ac.in/rm_2016-17/intern/intern_student",
    "jobsUrl": "http://tnp.dtu.ac.in/rm_2016-17/intern/intern_student/job_openings",
    "year": "2K16",
    "notifications_table": "rm-internship-notifications",
    "jobs_table": "rm-internship-jobs",
} if type == "internship" else {
    "loginUrl": "http://tnp.dtu.ac.in/rm_2016-17/login",
    "username_field": "student_username_rollnumber",
    "password_field": "student_password",
    "notifsUrl": "http://tnp.dtu.ac.in/rm_2016-17/student",
    "jobsUrl": "http://tnp.dtu.ac.in/rm_2016-17/student/job_openings/",
    "year": "2K15",
    "notifications_table": "rm-placement-notifications",
    "jobs_table": "rm-placement-jobs"
}

getHash = lambda str: hashlib.md5(str.encode()).hexdigest()

def getAccount(type):
    table = dynamodb.Table('rm-account')
    account = table.get_item(Key={
        'type': type
    })['Item']
    return account

def login(type, account):
    params = getParams(type)
    browser = RoboBrowser(history=True, parser="html.parser")
    browser.open(params["loginUrl"])
    form = browser.get_form(0)

    if not form:
        raise ValueError("Couldn't login")

    form[params["username_field"]].value = account['username']
    form[params["password_field"]].value = account['password']
    browser.submit_form(form)
    browser.open(params["notifsUrl"])
    return browser

def getNotifications(type):
    params = getParams(type)
    table = dynamodb.Table(params['notifications_table'])
    account = getAccount(type)
    browser = login(type, account)
    browser.open(params["notifsUrl"])
    soup = browser.parsed

    ul = soup.find('ul',attrs={'class':'timeline'})

    if not ul:
        raise ValueError("Couldn't open Notifications page")

    li_time_label = ul.find_all('li',attrs={'class':'time-label'})
    div_timeline_item = ul.find_all('div',attrs={'class':'timeline-item'})

    for i in range(len(li_time_label)):
        date = li_time_label[i].text.strip(' \t\n\r')
        time = div_timeline_item[i].span.text.strip(' \t\n\r').replace("&nbsp","").replace(";","")
        timelineHeader = div_timeline_item[i].find('h4',attrs={'class':'timeline-header'}).text.strip(' \t\n\r')
        timelineBody = div_timeline_item[i].find('div',attrs={'class':'timeline-body'}).text
        timelineHeaderUp = div_timeline_item[i].find('h3',attrs={'class':'timeline-header up'}).text.strip(' \t\n\r')
        timelineHeaderUp = timelineHeaderUp[len("Posted by : \n              \n              "):]
        key = getHash(date + time + timelineHeader + timelineBody[:5])
        if 'Item' not in table.get_item(Key={'key':key}):
            table.put_item(Item={
                "key": key,
                "date": date,
                "time": time,
                "heading": timelineHeader,
                "body": timelineBody,
                "poster": timelineHeaderUp
            })
    return "Notifications parsed"

def getJobs(type):
    params = getParams(type)
    table = dynamodb.Table(params['jobs_table'])
    account = getAccount(type)
    browser = login(type, account)

    browser.open(params["jobsUrl"])
    soup = browser.parsed

    table_jobopenings = soup.find('table',attrs={'id':'jobs_search'})

    if not table_jobopenings:
        raise ValueError("Couldn't open jobs page")

    trs = table_jobopenings.find_all('tr')

    for i in range(1, len(trs)):
        tds = trs[i].find_all('td')
        if tds[3].find('i')['class'][1] == 'fa-check':
            key = getHash(tds[0].text)
            if 'Item' not in table.get_item(Key={'key':key}):
                table.put_item(Item={
                    "key": key,
                    "name": tds[0].text,
                    "appDeadline": tds[2].text,
                    "dateOfVisit": tds[6].text,
                    "link": trs[i]['onclick'].replace("void window.open('","").replace("')",""),
                })
    return "Jobs parsed"

def handler(event, context):
    try:
        logger.info(event)
        type = event['type']
        function = event['function']
        if function == 'notifications':
            return(getNotifications(type))
        elif function == 'jobs':
            return(getJobs(type))
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise


handler({
    'type': 'placement',
    'function': 'notifications'
}, {})

