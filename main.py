import urllib.request
import requests
import sys
from lxml import html

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
    if isValue:
        return astr

    ret = ''
    for c in astr:
        if c.isnumeric() or c == '.':
            ret = ret + c
        else: 
            break
    return ret


def parseAnnouncement(url):
    tree = html.fromstring(requests.get(url, headers = headers).text)
    kitchenSq = parseLiSpanElem(tree, "Площадь кухни", True)
    liveSq = parseLiSpanElem(tree, "Жилая площадь", True)
    floor = parseLiSpanElem(tree, "Этаж", True)
    maxFloor = parseLiSpanElem(tree, "Этажей в доме", True)
    houseType = parseLiSpanElem(tree, "Тип дома", False)
    roomAmount = parseLiSpanElem(tree, "Количество комнат", True)
    return {
        'kitchenSq': kitchenSq,
        'liveSq': liveSq,
        'floor': floor,
        'maxFloor': maxFloor,
        'houseType': houseType,
        'roomAmount' : roomAmount
    }
    
print(parseAnnouncement(sys.argv[1]))
# print(parseLiSpanElem("fuck", "you"))
