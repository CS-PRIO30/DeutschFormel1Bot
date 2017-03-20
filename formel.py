# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import feedparser
from telegraphapi import Telegraph
import telegram
from mtranslate import translate

telegraph = Telegraph()
telegraph.createAccount("PythonTelegraphAPI")
TOKEN_TELEGRAM = '358045589:AAH-Bzm42xxEAeGZRLwDPsmQTSNZMKqBBrU' #DeutschFormel1Bot
MY_CHAT_ID_TELEGRAM = 31923577
bot = telegram.Bot(TOKEN_TELEGRAM)

entries = feedparser.parse('http://www.motorsport-total.com/rss_f1.xml').entries

url = entries[0].link
html = urllib.urlopen( url ).read()
bsObj = BeautifulSoup( html, "lxml" )

articleImage = bsObj.findAll("meta",{"property":"og:image"})[0].attrs["content"]
articleTitle = bsObj.findAll("meta",{"property":"og:title"})[0].attrs["content"].encode('utf-8')
articleDescription = bsObj.findAll("meta",{"property":"og:description"})[0].attrs["content"]
articleUrl = bsObj.findAll("meta",{"property":"og:url"})[0].attrs["content"]
articleContent = bsObj.findAll("div",{"class":"newstext","itemprop":"articleBody"})[0]

string = ""
for p in bsObj.findAll("div",{"class":"newstext","itemprop":"articleBody"})[0].findAll("p"):
	paragraph = str(p.get_text().encode("utf-8"))
	string = string + paragraph #+ "<i>" + translate( paragraph, "en", "de" ).encode("utf-8")) + "</i>"

string = string.replace("(Motorsport-Total.com) - ","")

chat_id_List = []
chat_id_List.append(31923577)
chat_id_List.append(227004432)



def sendTelegraph( articleImage, articleTitle, articleContent ):
	global MY_CHAT_ID_TELEGRAM
	stringAll = ""
	stringList = string.split(".")
	for paragraph in stringList:
		stringAll = stringAll + "<h4><b>" + paragraph.strip() + "</b></h4>" + "<i><u>" + str(translate( paragraph.strip(),"en","de" )) + "</u></i>"
		
	html_content = "<h4><b>" + articleTitle + "</b></h4>" + "<i><u>" + str( translate(articleTitle,"en","de") ) + "</u></i>\n" + "<a href=\"" + articleUrl + "\">LINK</a>" + "\n" + stringAll
	
	page = telegraph.createPage( title="Formel-1",  html_content= html_content, author_name="f126ck" )
	url2send = 'http://telegra.ph/{}'.format(page['path'])
	for chat_id in chat_id_List:
		try:
			bot.sendMessage(parse_mode = "Html", text = "<b>" + articleTitle + "</b>" + "\n" + url2send ,chat_id=chat_id)
		except:
			pass
sendTelegraph( articleImage, articleTitle, string )
