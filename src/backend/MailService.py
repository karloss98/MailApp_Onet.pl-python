import requests
from bs4 import BeautifulSoup
import json
import re

# DRAFTS_ID = 618753
# SPAM_ID = 618754
# SENT_ID = 618755
# TRASH_ID = 618756
# INBOX_ID = 618757
# NOTIFICATION_ID = 1112931
# OFFERS_ID = 1112932
# SOCIAL_ID = 1112933


foldersId = {
    'drafts': 0,
    'spam': 0,
    'sent': 0,
    'trash': 0,
    'inbox': 0,
    'notification': 0,
    'offers': 0,
    'social': 0,
}

def get_foldersid_from_api():
    url = 'https://api.poczta.onet.pl/api/folder'
    response = session.get(url)
    push_data_into_json = json.loads(response.text)


    foldersId['drafts'] = push_data_into_json['system']['drafts']['fid']
    foldersId['spam'] = push_data_into_json['system']['spam']['fid']
    foldersId['sent'] = push_data_into_json['system']['sent']['fid']
    foldersId['trash'] = push_data_into_json['system']['trash']['fid']
    foldersId['inbox'] = push_data_into_json['system']['inbox']['fid']
    foldersId['notification'] = push_data_into_json['smart']['notification']['fid']
    foldersId['offers'] = push_data_into_json['smart']['offers']['fid']
    foldersId['social'] = push_data_into_json['smart']['social']['fid']

    print(foldersId)

blackListOfSender = ['mailingi@onet.pl', 'mailing@mailing.gg.pl', '29998@implebot.net', 'sensei@zdobadzkobiete.pl', 'noreply@resman.pl',
                     'mancer@mancer.pl', 'portal@terazmatura.pl', 'noreply@databases.network', 'tchibo@databases.network', 'info@trecnutrition.com',
                     'redakcja@ang.pl', 'trajektoria@trajektoria.home.pl', 'newsletter@jakzdacmaturezmatematyki.pl', 'newsletter@matura2017.com.pl',
                     'rekrutacja@wsiz.rzeszow.pl', 'marketing@wsiz.rzeszow.pl', 'uncleuwo@gmail.com', 'maciej@maciejmoroz.pl', 'info@rusz-dupe.pl',
                     'amen-ra@militaria-1418.com', 'j@sukces.pl', '67931@implebot.net', 'kontakt@atrakcyjnyfacet.pl', 'info@kreatormilionerow.pl',
                     'elfie@hotelcastelverde.com', 'no-reply@lepszytrener.pl', 'finnobarr@masuperette.com', 'newsletter@neonet.pl',
                     'kolenkoa@lespouilles.com', 'adrian@atrakcyjnyfacet.pl', 'krzysztof@wyzwanie90dni.pl']

session = requests.session()

def login(mail, password):

    login_url = "https://konto.onet.pl/login.html?app_id=poczta.onet.pl.front.onetapi.pl&state=https://poczta.onet.pl/"

    credentials = {
        'login': mail,
        'password': password
    }

    HEADERS = {'referer': 'https://www.onet.pl/'}
    session.post(login_url, headers=HEADERS, data=credentials)
    res = session.get('https://poczta.onet.pl/Odebrane')
    soup = BeautifulSoup(res.content, 'html.parser')
    email = str(soup.find('script', type='text/javascript').get_text()).split('=')
    # print(email[1])

    try:
        configUser = json.loads(email[1])
    except Exception:
        # configUser=''
        print(False)
        return False
    activeMail = configUser['email']
    print(activeMail)
    if activeMail == mail:
        print(True)
        # get_foldersid_from_api()
        return True
    else:
        print(False)
        return False
    # return activeMail


def moveToRubbishBin(folderName,table):
    print('trash id: ', foldersId['trash'])
    print('src mail: ', folderName)
    moveToTrashData = {"dstFolder": foldersId['trash'],
                       "srcMails": {foldersId[folderName]: table}}

    url_trash = 'https://api.poczta.onet.pl/api/mail/?mailsGroup=1'
    test1 = session.options(url_trash)

    moveToKosz = session.patch(url_trash,   json=moveToTrashData)
    print('test1: ' + str(test1.status_code))
    print('czy przeniesiono: ' + str(moveToKosz.status_code))


def emptyRubbishBin():
    deleteAllUrl = 'https://api.poczta.onet.pl/api/mail/all/618756'
    deleteAction = session.delete(deleteAllUrl)
    print(deleteAction.content)
    print(deleteAction.status_code)
    if deleteAction.status_code == requests.codes.ok:
        return 'usunięto'

    else:
        return False


def getFoldersInfo():
    folderInfoUrl = 'https://api.poczta.onet.pl/api/folder'
    info = session.get(folderInfoUrl)
    entireInfoFolders = json.loads(info.text)
    namesFolder = ['drafts', 'spam', 'sent', 'trash', 'inbox', 'notification', 'offers', 'social']

    countFolder = [entireInfoFolders['system']['drafts']['count'],
                   entireInfoFolders['system']['spam']['count'],
                   entireInfoFolders['system']['sent']['count'],
                   entireInfoFolders['system']['trash']['count'],
                   entireInfoFolders['system']['inbox']['count'],
                   entireInfoFolders['smart']['notification']['count'],
                   entireInfoFolders['smart']['offers']['count'],
                   entireInfoFolders['smart']['social']['count']]
    return dict(zip(namesFolder, countFolder))


def scanFolderForUnwantedEmails(folderId, ):
    folderName=''
    unwantedEmailsTable = []
    for name, id in foldersId.items():
        if folderId == id:
            folderName = name
            break

    countEmailsInGivenFolder = getFoldersInfo()[folderName]
    print(countEmailsInGivenFolder)

    url = 'https://api.poczta.onet.pl/api/mail?sortDir=desc&sort=date&page=1&limit={}&folderId={}'.format(countEmailsInGivenFolder, folderId)
    entireFolderInfo = json.loads(session.get(url).text)
    iteration = 0
    for i, v in enumerate(entireFolderInfo):
        # print(i)
        dirtyEmail = entireFolderInfo[i]['from']
        print(dirtyEmail)
        if dirtyEmail == '':
            unwantedEmailsTable.append(entireFolderInfo[i]['mid'])
            continue
        clearEmail = re.search(r'<(.*)>', dirtyEmail).group(1)
        print(clearEmail)
        print(clearEmail[-2:])
        if (clearEmail in blackListOfSender or clearEmail[-2:]=='ru'):
            unwantedEmailsTable.append(entireFolderInfo[i]['mid'])
            iteration += 1

    print('ilosc niechcianych maili',len(unwantedEmailsTable))
    print('iteration', iteration)
    moveToRubbishBin(folderName, unwantedEmailsTable)


def send_mail_by_session(receiver, title, content, sender):

    deliver = [{'email': receiver,}]

    url = 'https://api.poczta.onet.pl/api/mail/send'
    headers_ = {'origin': 'https://www.onet.pl',
                'referer': 'https://poczta.onet.pl/'}
    payload = {#'attachments': [],
               # 'bcc':[],
               # 'cc': [],
               'deliveryReceipt': 0,  # not required
               'fromEmail': sender, # required
               'fromName': '',  # required
                # 'html': content, # not required
               'priority': 0,
               'readReceipt': 0,
               'saveSend': 1, # required
               'subject': title, #required
               'text': content,    #not required
               'to': deliver

               }


    r = session.post(url, headers=headers_, json=payload)
    print(r.content, r.status_code)


def logout():
    logoutUrlRequest = 'https://poczta.onet.pl/auth.html?state=logout'
    logout = session.get(logoutUrlRequest)
    print('status code:', str(logout.status_code))
    session.close()
    if logout.status_code == requests.codes.ok:
        return 'logout correctly'
    else:
        return False


def getProfileDetails(t):
    print(t)
    url = 'https://konto.onet.pl/api/profile'
    headers = {'referer': 'https://konto.onet.pl/'}

    res = session.get(url, headers=headers)
    print(res.content)


def getSingleMail(id):
    url = 'https://api.poczta.onet.pl/api/mail/{}'.format(id)

    mail = session.get(url)
    entire_mail = json.loads(mail.text)
    # print(entire_mail)

    from_sender = entire_mail['from']['email']
    title = entire_mail['subject']
    content = entire_mail['html']

    content = BeautifulSoup(content, 'html.parser').text
    return from_sender, title, content


def getJsonMails(page, folderId):
    url = 'https://api.poczta.onet.pl/api/mail?sortDir=desc&sort=date&page={}&limit={}&folderId={}'.format(page, 10, folderId)
    get = session.get(url)
    data_to_print = json.loads(get.text)
    # print(len(data_to_print))
    return data_to_print


