# -*- coding: utf-8 -*-


'''

change token

'''

from bs4 import BeautifulSoup
from urllib.request import urlopen #http://stackoverflow.com/questions/2792650/python3-error-import-error-no-module-name-urllib2#2792652
import feedparser
from telegraphapi import Telegraph
import telegram
from mtranslate import translate
import time
import os
from gtts import gTTS
import re

telegraph = Telegraph()
telegraph.createAccount("PythonTelegraphAPI")
TOKEN_TELEGRAM = '358045589:AAH-Bzm42xxEAeGZRLwDPsmQTSNZMKqBBrU' #DeutschFormel1Bot
MY_CHAT_ID_TELEGRAM = 31923577
bot = telegram.Bot(TOKEN_TELEGRAM)

try:
    update_id = bot.getUpdates()[0].update_id
except IndexError:
    update_id = None

print(update_id)
allUrl = []

def populateallUrl():
	lst = os.listdir("LOG/")
	for filename in lst:
		f = open("LOG/" + filename, "r")
		rows = f.read().split("\n")
		f.close()
		for row in rows:
			allUrl.append( row )

allRssFeed = []

def addRssFeedFromFile():
	f = open("rss_de.txt")
	rows = f.read().split("\n")
	for row in rows:
		if row[0] != "#":
			allRssFeed.append( row )
	f.close()
	
def get_nth_article():
	print(allRssFeed)
	for feed in allRssFeed:
		
		entries = feedparser.parse( feed ).entries
		print("feed " + feed)
		#print("entries" + entries[0])
		for i in reversed( range(10) ):
			try:
				url = entries[i].link
			except:
				print("Error while parsing " + feed)
				continue
			#url = "http://www.motorsport-total.com/f1/news/2017/04/zukunft-der-formel-1-haas-will-ein-oktoberfest-17040207.html"
			print(url)
			if url not in allUrl:
				print("notinallUrl")
				f = open("LOG/"+ feed.split("/")[-1] + ".txt","a")
				f.write( url + "\n" )
				f.close()
				allUrl.append( url )
				html = urlopen( url ).read()
				bsObj = BeautifulSoup( html, "html.parser" )

				articleImage = bsObj.findAll("meta",{"property":"og:image"})[0].attrs["content"]
				#print(articleImage)
				articleTitle = bsObj.findAll("meta",{"property":"og:title"})[0].attrs["content"]
				articleUrl = bsObj.findAll("meta",{"property":"og:url"})[0].attrs["content"]
				articleContent = bsObj.findAll("div",{"class":"newstext"})[0]
				try:
					boldArticleContent = articleContent.findAll("h2",{"class":"news"})[0].get_text()
				except IndexError:
					boldArticleContent = ""
				#remove shit from html, tags not accepted by Telegraph API
				[section.extract() for section in articleContent.findAll('section')]
				[span.extract() for span in articleContent.findAll('span')]
				[script.extract() for script in articleContent.findAll('script')]
				[noscript.extract() for noscript in articleContent.findAll('noscript')]
				[iframe.extract() for iframe in articleContent.findAll('iframe')]
				[blockquote.extract() for blockquote in articleContent.findAll('blockquote')]
				
				#print(boldArticleContent)
				#quit()
				string = ""
				for p in articleContent.findAll("p"):
					f = open("LADRO.txt","a")
					f.write("<INIZIO>\n\t" + str(p) + "\n</INIZIO>\n\n")
					f.close()
					paragraph = p.get_text()
					string = string + paragraph + "\n"
					
				string = string.replace("(Motorsport-Total.com) - ","")
				f = open("string.txt","w")
				f.write(str(string))
				f.close()
				
				#print(string)
				articleTitle = articleTitle.replace("- Motorrad bei Motorsport-Total.com","")
				articleTitle = articleTitle.replace("- WEC bei Motorsport-Total.com","")
				articleTitle = articleTitle.replace("- DTM bei Motorsport-Total.com","")
				articleTitle = articleTitle.replace("- WTCC bei Motorsport-Total.com","")
				articleTitle = articleTitle.replace("- Oldtimer bei Motorsport-Total.com","")
				
				articleTitle = articleTitle.replace("- Motorrad bei Motorsport-Total.com","")
				articleTitle = articleTitle.replace("- Rallye bei Motorsport-Total.com","")
				articleTitle = articleTitle.replace("- Formelsport bei Motorsport-Total.com","")
				
				articleTitle = articleTitle.replace("- US-Racing bei Motorsport-Total.com","")
				articleTitle = articleTitle.replace("- Mehr Motorsport bei Motorsport-Total.com","")
				sendTelegraph( articleImage, articleTitle, boldArticleContent, articleUrl, string, feed )
			else:
				print("Found no new link.")
				
chat_id_List = []
def addChatIdFromFile():
	f = open("chat_id.txt")
	rows = f.read().split("\n")
	for row in rows:
		if row != "":
			chat_id_List.append( int(row) )
	f.close()
addChatIdFromFile()
print(chat_id_List)

MY_ITALIAN_READING_PER_MINUTE = 235

def getTimeReadingString( words ):
	lung = len(words)
	#print( str( len(words) )	)
	minutes = len(words) / MY_ITALIAN_READING_PER_MINUTE
	#print(	"minutes " + str(minutes)	)
	if minutes == 0:
		return str(lung) + " parole.\n~1 min."
	timeReading = str(lung) + " parole.\n~" + str( int(minutes) )  + " min, " + str( round( (minutes-int(minutes) ) * 60 ) ) + " sec"
	return timeReading
	#print(timeReading)

def sendTelegraph( articleImage, articleTitle, boldArticleContent, articleUrl, string ,feed ):
	global MY_CHAT_ID_TELEGRAM
	html_content = ""
	boldArticleContent = boldArticleContent + "."
	articleTitle = articleTitle + "."
	stringAll = ""
	string = string.replace("ANZEIGE","")
	string = string.replace(u'\xa0', u'')
	string = re.sub('\t+', '', string)
	string = re.sub('\t+ ', '', string)
	string = re.sub('\n +\n+ ', '\n', string)
	string = re.sub('<[^<]+?>', '', string)
	string = re.sub('\n+','\n', string).strip().replace(">","")
	string = re.sub('\n +\n', '\n', string)
	
	words = ''.join(c if c.isalnum() else ' ' for c in articleTitle + boldArticleContent + string).split() #http://stackoverflow.com/questions/17507876/trying-to-count-words-in-a-string
	timeReading = getTimeReadingString( words )
	stringToBetranslated = articleTitle + " " + boldArticleContent + " " + string
	
	imageLink = "<a href=\"" + articleImage + "\" target=\"_blank\"><img src=\"" + articleImage + "\"></img></a>"
	try:
		html_content = "<h4><b>" + articleTitle + "</b>" + imageLink + "</h4>" + "<b>" + boldArticleContent + "</b>\n" + "<a href=\"" + articleUrl + "\">LINK</a>\n\n" + string + "\n\n\n" + stringTranslated 
	except:
		pass
	#stringList = stringToBetranslated.split(". ")
	stringList = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", stringToBetranslated)
	for paragraph in stringList:
		try:
			html_content = html_content + "<strong>" + paragraph + "</strong>" + "\n<i>" + translate( paragraph, "en","de" ) + "</i>" + "\n\n"
		except:
			pass
	print(html_content)
	html_content = imageLink + html_content
	page = telegraph.createPage( title = articleTitle,  html_content= html_content, author_name="f126ck" )
	url2send = 'http://telegra.ph/' + page['path']
	catIntro = getCategoryIntro( feed )
	
	#tts = gTTS(text = articleTitle + string, lang='de')
	#tts.save( "AUDIO/" + articleTitle + ".mp3")
	
	for chat_id in chat_id_List:
		print("sending to chat_id: " + str(chat_id))
		try:
			#f = open( "AUDIO/" + articleTitle + ".mp3", "rb")
			bot.sendMessage(parse_mode = "Html", text =  catIntro +  "<b>" + articleTitle + "</b>" + " " + "<a href=\"" + url2send + "\">.</a>\n" + timeReading, chat_id = chat_id)
			#bot.sendAudio( audio = f, chat_id = chat_id)
			#f.close()
		except:
			print("1 message was not sent to recipient" )

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
			print("error get_new_users")
		update_id = update.update_id + 1
		try:
			if update.message.chat_id:  # your bot can receive updates without messages
				if chat_id not in chat_id_List:
					#print "New user added with chat_id: " + str(chat_id)
					chat_id_List.append( int(chat_id) )
					f = open("chat_id.txt","a")
					f.write( str(chat_id) + "\n" )
					f.close()
		except:
			print("error getUpdates")
	bot.getUpdates(offset=update_id,timeout=0)

def main():
	populateallUrl()
	addRssFeedFromFile()
	while True:
		get_new_Users()
		get_nth_article()
		#print "(!) sleep"
		time.sleep(300)

main()
