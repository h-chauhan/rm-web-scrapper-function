import requests

MESSENGER_API = 'https://api.dturmupdates.me/messenger/'

notificationTemplate = lambda date, time, heading, body, poster: \
"""
🔔 Notification Update

🕑 {date} {time}

➡️  {heading}
{body}

📝  Posted by: {poster}
""".format(date=date, time=time, heading=heading, body=body, poster=poster)

jobTemplate = lambda name, dateOfVisit, appDeadline, link: \
"""
👨‍💻  Job Update

🏢  {name}

📆  Date of visit: {dateOfVisit}

⚠️  Last date to apply: {appDeadline}

🔗  Apply here: {link}
""".format(name=name, dateOfVisit=dateOfVisit, appDeadline=appDeadline, link=link)

def sendMessage(label, message):
    response = requests.post(MESSENGER_API, data={
        'label': label,
        'textMessage': message
    })
    return response.json
