import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import zipfile
from urllib.request import urlopen
import datetime
from xml.etree.ElementTree import parse

print('started')
json_data = {"password": "RAMTRX1500", "regulation": True, "email": "Rakhmanov-2019@list.ru"}
response = requests.post('https://www.sima-land.ru/api/v5/signin', json=json_data)
token = response.json().get('token')
print('token initialized')
session = requests.Session()
retry = Retry(connect=2, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
print('trying to get xml...')
zip = zipfile.ZipFile('ostatki.zip')
zip.extractall()
import psutil
print('trying to parse xml...')
k = datetime.datetime.now()

xmldoc = parse('t.xml')
print(psutil.virtual_memory().percent)
print('starting main loop...')
print(datetime.datetime.now() - k)
for tag in xmldoc.iterfind('shop/offers/offer'):
    try:
        tag.remove(tag[1])
    except Exception:
        pass
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
    if int(tag.find('count').text) < 10:
        tag.find('count').text = '0'
    else:
        tag.find('count').text = str(response.json()['balance'])
xmldoc.write('t.xml', encoding='utf-8')
zf = zipfile.ZipFile("ostatki.zip", "w", compresslevel=8, compression=zipfile.ZIP_DEFLATED)
zf.write('t.xml', compresslevel=8)

files = {
    'file': open('ostatki.zip', 'rb'),
}
response = requests.post('https://sima-land-yandex.herokuapp.com/upload', files=files)
response = requests.post('https://puper-lis.herokuapp.com/upload', files=files)
response = requests.post('https://young-lis.herokuapp.com/upload', files=files)
print(response.json())
