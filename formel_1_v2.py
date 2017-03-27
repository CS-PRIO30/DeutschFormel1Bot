# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import feedparser
from telegraphapi import Telegraph
import telegram
from mtranslate import translate
import time
import os
from gtts import gTTS

telegraph = Telegraph()
telegraph.createAccount("PythonTelegraphAPI")
TOKEN_TELEGRAM = '358045589:AAH-Bzm42xxEAeGZRLwDPsmQTSNZMKqBBrU' #DeutschFormel1Bot
MY_CHAT_ID_TELEGRAM = 31923577
bot = telegram.Bot(TOKEN_TELEGRAM)
try:
    update_id = bot.getUpdates()[0].update_id
except IndexError:
    update_id = None

allUrl = []

def populateallUrl():
	lst = os.listdir("LOG/")
	for filename in lst:
		f = open("LOG/" + filename, "r")
		rows = f.read().split("\n")
		f.close()
		for row in rows:
			allUrl.append( row )

populateallUrl()
allRssFeed = []

def addRssFeedFromFile():
	f = open("rss_de.txt")
	rows = f.read().split("\n")
	for row in rows:
		allRssFeed.append( row )
	f.close()
	
addRssFeedFromFile()

def get_nth_article():
	#http://www.motorsport-total.com/rss_motorrad_MGP.xml
	#http://www.motorsport-total.com/rss_formelsport_GP2.xml
	#http://www.motorsport-total.com/rss_wec.xml
	#http://www.motorsport-total.com/rss_f1.xml
	
	for feed in allRssFeed:
		entries = feedparser.parse( feed ).entries
		for i in reversed( range(5) ):
			url = entries[i].link
			if url not in allUrl:
				f = open("LOG/"+ feed.split("/")[-1] + ".txt","a")
				f.write( url + "\n" )
				f.close()
				print str(i + 1) + ") Found new link: "  + url
				allUrl.append( url )
				html = urllib.urlopen( url ).read()
				bsObj = BeautifulSoup( html, "html.parser" )

				articleImage = bsObj.findAll("meta",{"property":"og:image"})[0].attrs["content"]
				articleTitle = bsObj.findAll("meta",{"property":"og:title"})[0].attrs["content"].encode('utf-8')
				articleDescription = bsObj.findAll("meta",{"property":"og:description"})[0].attrs["content"]
				articleUrl = bsObj.findAll("meta",{"property":"og:url"})[0].attrs["content"]
				articleContent = bsObj.findAll("div",{"class":"newstext"})[0]

				string = ""
				for p in bsObj.findAll("div",{"class":"newstext"})[0].findAll("p"):
					paragraph = p.get_text().encode("utf-8")
					string = string + paragraph #+ "<i>" + translate( paragraph, "en", "de" ).encode("utf-8")) + "</i>"
				string = string.replace("(Motorsport-Total.com) - ","")
				sendTelegraph( articleImage, articleTitle, articleUrl, string, feed )
			else:
				pass
				#print "Found no new link."
				
chat_id_List = []
def addChatIdFromFile():
	f = open("chat_id.txt")
	rows = f.read().split("\n")
	for row in rows:
		if row != "":
			chat_id_List.append( int(row) )
	f.close()
addChatIdFromFile()
print chat_id_List

def sendTelegraph( articleImage, articleTitle, articleUrl, string ,feed ):
	global MY_CHAT_ID_TELEGRAM
	stringAll = ""
	stringList = string.split(".")
	for paragraph in stringList:
		paragraph = paragraph.replace("&quot;","\"")
		print articleUrl
		
		stringAll = stringAll + "<h4><b>" + paragraph.strip().encode("utf-8") + ".</b></h4>" + "<i><u>" + translate( paragraph.strip(),"en","de" ).encode("utf-8") + ".</u></i>"
		
	html_content = "<h4><b>" + articleTitle.encode("utf-8") + "</b></h4>" + "<i><u>" + translate(articleTitle,"en","de").encode("utf-8") + "</u></i>\n" + "<a href=\"" + articleUrl.encode("utf-8") + "\">LINK</a>" + stringAll.encode("utf-8")
	
	page = telegraph.createPage( title="Formel-1",  html_content= html_content, author_name="f126ck" )
	url2send = 'http://telegra.ph/{}'.format(page['path'])
	catIntro = getCategoryIntro( feed )
	
	tts = gTTS(text = articleTitle + string, lang='de')
	tts.save( "AUDIO/" + articleTitle + ".mp3")
	
	for chat_id in chat_id_List:
		print "sending to chat_id: " + str(chat_id)
		try:
			f = open( "AUDIO/" + articleTitle + ".mp3", "rb")
			bot.sendMessage(parse_mode = "Html", text = catIntro +  "<b>" + articleTitle + "</b>" + "\n" + url2send ,chat_id = chat_id)
			bot.sendAudio( audio = f, chat_id = chat_id)
			f.close()
		except:
			print "1 message was not sent to recipient" 

def getCategoryIntro( feed ):
	category = ""
	if "GP2" in feed.upper():
		category = "GP2"
	if "WEC" in feed.upper():
		category = "WEC"
	if "F1" in feed.upper():
		category = "F1"
	if "MGP" in feed.upper():
		category = "MOTOGP"
	if category != "":
		return "[" + category + "]" + "\n"
	else:
		return ""

def get_new_Users():
	global update_id
	for update in bot.getUpdates(offset=update_id, timeout=10):
		try:
			chat_id = update.message.chat_id
		except:
			print "error get_new_users"
		update_id = update.update_id + 1
		try:
			if update.message.chat_id:  # your bot can receive updates without messages
				if chat_id not in chat_id_List:
					print "New user added with chat_id: " + str(chat_id)
					chat_id_List.append( int(chat_id) )
					f = open("chat_id.txt","a")
					f.write( str(chat_id) + "\n" )
					f.close()
		except:
			print "error getUpdates"
	bot.getUpdates(offset=update_id,timeout=0)

def main():
	while True:
		get_new_Users()
		get_nth_article()
		print "(!) sleep"
		time.sleep(300)

main()
