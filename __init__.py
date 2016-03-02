import requests
import subprocess
import os
import json
from bs4 import BeautifulSoup

WorkSpace='.'
ComicCDNHost='http://images.dmzj.com/'

def MakeFileSystemReady():
	system('md _DataBase')

def GenerateUID(URL):#http://www.dmzj.com/info/zhenlizhitu.htmlhttp://www.dmzj.com/view/zhenlizhitu/37273.html
	Stage=URL.find('http://www.dmzj.com/')
	if Stage!=-1:
		Stage=URL.find('/info/')
		if Stage!=-1:
			ToReturn=URL.split('/info/')[1].split('.')[0]
			return ToReturn
		else:
			ToReturn=URL.split('/view/')[1].split('/')[0]
			return ToReturn
	else:
		return 'Error!'

def CreatURL(UID):
	#http://www.dmzj.com/info/zhenlizhitu.html
	return 'http://www.dmzj.com/info/'+UID+'.html'

def GetCover(URL):
	Page=requests.get(URL)
	Page=Page.content
	PageSoup=BeautifulSoup(Page)
	PageSoup=PageSoup.find('div',{'class':'comic_i_img'})
	CoverURL=PageSoup.a.img['src']
	print CoverURL
	#<div class="comic_i_img">

def MakeIndex(URL):
	Page=requests.get(URL).content
	PageSoup=BeautifulSoup(Page)
	PageSoup=PageSoup.find('ul',{'class':'list_con_li autoHeight'}).findAll('li')
	ToReturn=[]
	for liItem in PageSoup:
		Link=liItem.a['href']
		Title=liItem.find('span',{'class':'list_con_zj'})
		ToReturn.append([Link,Title])
	return ToReturn

def Downloader(IndexItem):
	Page=requests.get(IndexItem[0])
	Page=Page.content
	PageSoup=BeautifulSoup(Page)
	Script=PageSoup.find('script',{'type':'text/javascript'}).text.replace('return p','console.log(p)')
	#Script=unicode(Script.strip(codecs.BOM_UTF8),'UTF-8')
	FileHandle=open('Script.js','w')
	Script=Script.encode('UTF-8').strip().split('\n')[2]
	FileHandle.write(Script)
	#content = unicode(q.content.strip(codecs.BOM_UTF8), 'utf-8')
	FileHandle.close()
	RunScript='node Script.js'
	Result=subprocess.check_output(RunScript,shell=True)
	os.remove('Script.js')
	Result=Result.replace('var pages=pages=\'','').replace('"}\';','"}')
	Json=json.loads(Result)
	ChapterOrder=Json['chapter_order']
	ChapterOrderStr=str(Json['chapter_order'])
	ChapterName=Json['chapter_name']
	ID=Json['id']
	ToAdd=4-len(str(Json['chapter_order']))
	while(ToAdd!=0):
		ChapterOrderStr='0'+ChapterOrderStr
		ToAdd-=1
	URLs=Json['page_url'].split('\r\n')
	ComicName=Json['comic_name']
	PictureNumber=Json['picnum']
	try:
		os.path.mkdir('_DataBase/'+ComicName)
	except:
		pass
	Counter=1
	print len(URLs)
	for URLItem in URLs:
		File=requests.get(ComicCDNHost+URLItem,headers={'referer':'http://www.dmzj.com/'})
		File=File.content
		CounterStr=str(Counter)
		ToAdd=3-len(str(Counter))
		while(ToAdd!=0):
			CounterStr='0'+CounterStr
			ToAdd-=1
		FileName=ChapterOrderStr+'_'+CounterStr+'.jpg'
		FileHandle=open('_DataBase/'+str(ID)+'/'+FileName,'wb')
		FileHandle.write(File)
		FileHandle.close()
		Counter+=1

def StartTask(Condition,Index,Path):#All#,Part#1-,Select#
	ConditionFormat=Condition.lower()
	if ConditionFormat=='all':
		pass
	else:
		if ConditionFormat.split('#')[0]=='part':
			ConditionFormat=ConditionFormat.split('#')[1]
			if ConditionFormat.split('-')[1]=='':
				Index=Index[:int(ConditionFormat.split('-')[0])]
			else:
				if ConditionFormat.split('-')[0]=='':
					Index=Index[int(ConditionFormat.split('-')[1]):]
				else:
					pass
		else:
			if ConditionFormat.split('#')[0]=='select':
				NewIndex=[]
				ConditionFormat=ConditionFormat.split('#')[1]
				ConditionFormat=ConditionFormat.split(',')
				for Item in ConditionFormat:
					NewIndex.append(Index[int(Item)-1])
				Index=NewIndex
			else:
				pass
	#Downloader

Downloader(['http://manhua.dmzj.com/fdbxtgcs/33851.shtml',''])
#GetCover('http://www.dmzj.com/info/zhenlizhitu.html')
#GenerateUID('http://www.dmzj.com/info/zhenlizhitu.html')
#MakeIndex('http://www.dmzj.com/info/zhenlizhitu.html')
#StartTask('Select#2,3',MakeIndex('http://www.dmzj.com/info/zhenlizhitu.html'),2333)