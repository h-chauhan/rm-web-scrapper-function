from robobrowser import RoboBrowser
from google.cloud import firestore

from params import getParams

db = firestore.Client();

def getAccount(type):
    return db.collection('accounts').document(type).get().to_dict()

def login(type, account):
    params = getParams(type)
    browser = RoboBrowser(history=True, parser='html.parser')
    browser.open(params['loginUrl'])
    form = browser.get_form(0)

    if not form:
        raise ValueError("Couldn't login")

    form[params['username_field']].value = account['username']
    form[params['password_field']].value = account['password']
    browser.submit_form(form)
    browser.open(params['notifsUrl'])

    print('Logged in with account: {}'.format(account))

    return browser