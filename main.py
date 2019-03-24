import urllib.request
import requests
import sys
from lxml import html
from six.moves.html_parser import HTMLParser
import re

headers = {
    'user-agent' :"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/72.0.3626.121 Chrome/72.0.3626.121 Safari/537.36",
    "authority": "www.avito.ru",
    "method": "GET",
    'path': '/perm/kvartiry/prodam/2-komnatnye',
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6"
}

rootUrl = "https://avito.ru"

def parseAnnouncementLinks(url):
    urls = []
    reqUrl = url 
    print('start to parse announcements links')
    while reqUrl != None:
        print('read from link: ' + reqUrl)
        resp = requests.get(reqUrl, headers = headers).text
        tree = html.fromstring(resp)
        parent = tree.xpath("""//a[@itemprop="url"]""")
        if parent == None: 
            print("Can't find any link in the url: " + reqUrl)
            break;

        parentUrls = list(map(lambda x: x.attrib['href'], parent))
        urls.append(parentUrls)
        nextPage = tree.xpath("""//a[@class="pagination-page js-pagination-next"]""")
        if nextPage == None:
            break;
        reqUrl = rootUrl + nextPage[0].attrib['href']
        break
    return urls

def parseLiSpanElem(tree, label, isValue):
    astr = str(html.tostring(tree.xpath('//li[span[contains(.,"' + label + '")]]')[0]), 'UTF-8')
    astr = astr[astr.find('span>') + 5:astr.find('</li>')].strip()
    if not isValue:
        return astr

    ret = ''
    for c in astr:
        if c.isnumeric() or c == '.':
            ret = ret + c
        else: 
            break
    return ret

def parseAddress(tree):
    return tree.xpath('//span[@itemprop="streetAddress"]')[0].text.strip() 

def parseOwnerName(tree):
    return tree.xpath('//div[@class="seller-info-col"]/div[@class="seller-info-value"]/div[@class="seller-info-name js-seller-info-name"]/a')[0].text.strip()

def parseSellerType(tree):
    return tree.xpath('//div[@class="seller-info-col"]/div[not(@*)]')[0].text.strip() 

def parseAnnouncement(url):
    htmlParser = HTMLParser()
    tree = html.fromstring(requests.get(url, headers = headers).text)
    kitchenSq = parseLiSpanElem(tree, "Площадь кухни", True)
    liveSq = parseLiSpanElem(tree, "Жилая площадь", True)
    floor = parseLiSpanElem(tree, "Этаж", True)
    maxFloor = parseLiSpanElem(tree, "Этажей в доме", True)
    houseType = htmlParser.unescape(parseLiSpanElem(tree, "Тип дома", False))
    roomAmount = parseLiSpanElem(tree, "Количество комнат", True)
    address = parseAddress(tree)
    owner = parseOwnerName(tree)
    ownerType = parseSellerType(tree)
    return {
        'kitchenSq': kitchenSq,
        'liveSq': liveSq,
        'floor': floor,
        'maxFloor': maxFloor,
        'houseType': houseType,
        'roomAmount' : roomAmount,
        'address': address,
        'owner' : owner,
        'ownerType' : ownerType
    }
    
def phoneDemixer(itemId, phoneId):
    if phoneId is None: 
        return "" 

    matches = re.findall('[0-9a-f]+', phoneId)
    itemIdIntVal = int(float(itemId))
    if itemIdIntVal % 2 == 0 :
        matches =  list(reversed(matches))

    anotherStr = "".join(matches) resultStr = '' for i in range(len(anotherStr)): if i % 3 == 0: resultStr += anotherStr[i] return resultStr


def getItemId(reqStr):
    itemIdStartIndex = reqStr.find('"itemID"')
    itemIdEndIndex = reqStr.find(',', itemIdStartIndex) 
    itemStr = reqStr[itemIdStartIndex:itemIdEndIndex]
    return itemStr[(itemStr.find(":") +1):]

def getPhoneId(reqStr):
    phoneStartInd = reqStr.find('avito.item.phone')
    phoneEndIndex = reqStr.find(';', phoneStartInd)
    phoneStr = reqStr[phoneStartInd:phoneEndIndex]
    phoneNumbFromIdx = phoneStr.find("'")
    phoneNumbToIdx = phoneStr.find("'", phoneNumbFromIdx + 1)
    return phoneStr[(phoneNumbFromIdx + 1):phoneNumbToIdx]

# headers for image request
# :authority: www.avito.ru
# :method: GET
# :path: /items/phone/1002138546?pkey=da2d8d282ba56db9300195305fe78665&vsrc=r
# :scheme: https
# accept: */*
# accept-encoding: gzip, deflate, br
# accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6
# referer: https://www.avito.ru/perm/kvartiry/2-k_kvartira_44_m_55_et._1002138546
# user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.75 Chrome/73.0.3683.75 Safari/537.36
# x-requested-with: XMLHttpRequest
