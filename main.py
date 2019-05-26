import hashlib
import sentry_sdk
from sentry_sdk.integrations.serverless import serverless_function

from scrapper import getNotifications, getJobs

sentry_sdk.init('https://afe5f72242f64022941a47e2e8c947fe@sentry.io/1412608')

@serverless_function
def handler(event):
    print(getNotifications('internship'))
    print(getJobs('internship'))
    print(getNotifications('placement'))
    print(getJobs('placement'))
    

