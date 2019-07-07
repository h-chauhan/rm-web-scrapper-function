from google.cloud import firestore
import hashlib

from params import getParams
from account import getAccount, login
from messenger import notificationTemplate, jobTemplate, sendMessage

db = firestore.Client()

getHash = lambda str: hashlib.md5(str.encode()).hexdigest()

def getNotifications(type):
    params = getParams(type)
    collectionRef = db.collection('{}-notifications'.format(type))

    account = getAccount(type)
    browser = login(type, account)
    browser.open(params['notifsUrl'])
    soup = browser.parsed

    ul = soup.find('ul',attrs={'class':'timeline'})

    if not ul:
        raise ValueError("Couldn't open Notifications page")

    li_time_label = ul.find_all('li',attrs={'class':'time-label'})
    div_timeline_item = ul.find_all('div',attrs={'class':'timeline-item'})

    for i in range(len(li_time_label)):
        date = li_time_label[i].text.strip(' \t\n\r')
        time = div_timeline_item[i].span.text.strip(' \t\n\r').replace('&nbsp','').replace(';','')
        heading = div_timeline_item[i].find('h4',attrs={'class':'timeline-header'}).text.strip(' \t\n\r')
        body = div_timeline_item[i].find('div',attrs={'class':'timeline-body'}).text
        poster = div_timeline_item[i].find('h3',attrs={'class':'timeline-header up'}).text.strip(' \t\n\r')
        poster = poster[len('Posted by : \n              \n              '):]
        key = '{} : {} : {}'.format(getHash(date + time + heading + body[:5]), date, time)

        docRef = collectionRef.document(key)
        if not docRef.get().exists:
            docRef.set({
                'key': key,
                'date': date,
                'time': time,
                'heading': heading,
                'body': body,
                'poster': poster
            })
            sendMessage(label=type, message=notificationTemplate(date, time, heading, body, poster))
    return '{} notifications parsed'.format(type)

def getJobs(type):
    params = getParams(type)
    collectionRef = db.collection('{}-jobs'.format(type))

    account = getAccount(type)
    browser = login(type, account)

    browser.open(params['jobsUrl'])
    soup = browser.parsed

    table_jobopenings = soup.find('table',attrs={'id':'jobs_search'})

    if not table_jobopenings:
        raise ValueError("Couldn't open jobs page")

    trs = table_jobopenings.find_all('tr')

    for i in range(1, len(trs)):
        tds = trs[i].find_all('td')
        if tds[3].find('i')['class'][1] == 'fa-check':
            name = tds[0].text
            appDeadline = tds[2].text
            dateOfVisit = tds[6].text
            link = trs[i]['onclick'].replace("void window.open('", '').replace("')", '')

            docRef = collectionRef.document(name)
            if not docRef.get().exists:
                docRef.set({
                    'name': name,
                    'appDeadline': appDeadline,
                    'dateOfVisit': dateOfVisit,
                    'link': link,
                })
                sendMessage(label=type, message=jobTemplate(name, appDeadline, dateOfVisit, link))

    return '{} jobs parsed'.format(type)
