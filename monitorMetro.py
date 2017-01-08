# -*- encoding: utf-8 -*-

import sys
import telepot
import requests
import xmltodict
from zeep import Client
from pprint import pprint
from apscheduler.schedulers.blocking import BlockingScheduler


reload(sys)
sys.setdefaultencoding('utf8')

sched = BlockingScheduler()
userID = ''
apiTelegram = ''
apiWebhose = ''

def getNews(query):
    url = 'https://webhose.io/search?token=%s&format=json&q=%s' % (apiWebhose,query)
    r = requests.get(url)
    news = r.json()['posts']
    for post in range(0,3):
        msg = '%s\nURL: %s\nFonte: %s' %(news[post]['thread']['title'],news[post]['thread']['url'],news[post]['thread']['site_full'])
        sendNotify(msg)

def sendNotify(message):
    bot = telepot.Bot(apiTelegram)
    bot.sendMessage(userID, message)

@sched.scheduled_job('interval', minutes=60)
def getStatus():
    client = Client('http://apps.metrosp.com.br/api/diretodometro/v1/SituacaoLinhasMetro.asmx?WSDL')
    result = client.service.GetSituacaoTodasLinhas('B7758201-15AF-4246-8892-EAAFFC170515')
    diretodometro = xmltodict.parse(result)['diretodometro']
    for linha in diretodometro['linhas']['linha']:
        if 'Normal' not in linha['situacao']:
            msg = '%s esta parada, buscando ultimas noticias sobre esta linha...' % linha['nome']
            query = '%s metrô São Paulo' % linha['nome']
            sendNotify(msg)
            getNews(query)

sched.start()
