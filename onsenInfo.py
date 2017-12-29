# coding: utf-8
import re
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
callback = re.compile('callback\((.*)\);')
weekChar={"月曜":"mon","火曜":"tue","水曜":"wed","木曜":"thu","金曜":"fri","土曜":"sat","日曜":"sat","今日":"latest","最新":"latest"}
weekNum=["mon","tue","wed","thu","fri","sat","sat"]

def getTileList() :
    html = urlopen("http://www.onsen.ag/api/shownMovie/shownMovie.json")
    list = json.loads(html.read().decode('utf8'))
    return list["result"]

def parseTitleInfoLi( li ):
    ret = {
        "id" : li['id'],
        "data-kana" : li['data-kana'],
        "title" : li.find("h4",{"class":"listItem"}).string,
        "personality" :  li.find("p",{"class":"navigator listItem"}).string,
        "update" :  li.find("p",{"class":"update listItem"}).string,
        "thumbnail" :  li.find("p",{"class":"thumbnail listItem"}).find('img')['src']
    }
    guest = li.find("li",{"data-guest":True})
    if not guest == None:
        guest = guest.string
    ret["guest"] = guest
    return ret

def getTitleInfo(id):
    html = urlopen("http://www.onsen.ag/data/api/getMovieInfo/" + id)
    body = callback.search(html.read().decode('utf8')).group(1)
    list = json.loads(body)
    return list

def getTitleInfoOfDayNum(day,num,titles=None):
    if titles == None:
        titles = {}
        d = getDayId(day)
        if d == "latest" :
            titles = getNewTitle()
        else:
            titles = getTitleOfDay(d)
    ret=""
    title=titles[num]
    return title

def getTitleOfDay(day):
    html = urlopen("http://www.onsen.ag")
    bsObj = BeautifulSoup(html, "html.parser")
    titles = bsObj.findAll("li",{"data-week":day})
    ret = []
    for title in titles :
        ret.append(parseTitleInfoLi(title))
    return ret

def getNewTitle():
    html = urlopen("http://www.onsen.ag")
    bsObj = BeautifulSoup(html, "html.parser")
    titles = bsObj.findAll("li",{"class":"clr active newChecked"})
    ret = []
    for title in titles :
        ret.append(parseTitleInfoLi(title))
    return ret

def getDayId(day):
    return weekChar[day]

def getStringListOfDay(day,titles=None,yomi=False):
    if titles == None:
        titles = {}
        d = getDayId(day)
        if d == "latest" :
            titles = getNewTitle()
        else:
            titles = getTitleOfDay(d)
    num = 1
    ret=""
    for title in titles:
        if yomi :
            ret += "{0} {1} {2}\n".format(day,num,title["data-kana"])
        else :
            ret += "{0} {1} {2}\n".format(day,num,title["title"])
        num+=1
    return ret