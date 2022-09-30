import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import zipfile
from urllib.request import urlopen
import datetime
from xml.etree.ElementTree import parse


def main():
    print('started')
    json_data = {"password": "RAMTRX1500", "regulation": True, "email": "Rakhmanov-2019@list.ru"}
    response = requests.post('https://www.sima-land.ru/api/v5/signin', json=json_data)
    token = response.json().get('token')
    print('token initialized')
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    print('trying to get xml...')
    zip = zipfile.ZipFile('origin.zip')
    zip.extractall()
    import psutil
    print('trying to parse xml...')
    k = datetime.datetime.now()
    xmldoc = parse('ostatki.xml')
    print(psutil.virtual_memory().percent)
    print('starting main loop...')
    print(datetime.datetime.now() - k)
    root = xmldoc.getroot()
    root.attrib['date'] = str(datetime.datetime.now())[:-7]
    try:
        for tag in xmldoc.iterfind('shop/offers/offer'):
            response = session.get(
                f"https://www.sima-land.ru/api/v5/item/{tag.attrib['id']}",
                headers={
                    'accept': 'application/json',
                    'X-Api-Key': token,
                    'Authorization': token,
                },

                params={
                    'view': 'brief',
                    'by_sid': 'false',
                }
            )
            print(response.json()['sid'])
            if int(response.json()['balance']) < 15 or response.status_code != 200 or int(tag.find('count').text) < 10:
                tag.find('count').text = '0'
            else:
                tag.find('count').text = str(response.json()['balance'])

    except Exception as e:
        print(e)
        pass
    xmldoc.write('ostatki.xml', encoding='utf-8')
    files = {
        'file': open('ostatki.xml', 'rb'),
    }
    time.sleep(5)
    response = requests.post('https://sima-land-yandex.herokuapp.com/upload', files=files)
    print(response.json())


main()
