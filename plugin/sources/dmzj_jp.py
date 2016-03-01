#coding: utf-8

import re
import sys
from bs4 import BeautifulSoup

sys.path.append('..')

import libs.util as util
from libs.core import *

class Source:

    #http://manhua.dmzj.com/yiquanchaoren/19848.shtml#@page=1
    #http://manhua.dmzj.com/yiquanchaoren/
    @staticmethod
    def test(text):
        if len(re.findall('(https|http)://manhua\.dmzj\.com/.*?/',text))>0:
            return 'dmzj_jp'
        else:
            return False

    @staticmethod
    def version():
        return '%umname% plugin dmzj_jp. Version: 0.01.'

    @staticmethod
    def name():
        return 'dmzj_jp'

    def build_index_url(self):
        return 'http://manhua.dmzj.com/%s/' % (self.credential,)

    def get_credential(self,url):
        self.credential = re.findall('(https|http)://manhua\.dmzj\.com/(.*?)/',url)[0][1]
        return self.credential

    def __init__(self,url,choose_mode = False):

        #init credential
        self.get_credential(url)
        self.url = self.build_index_url()
        self.choose_mode = choose_mode

        respon = util.get(self.url)
        if respon:
            self.page = respon
            self.bs = BeautifulSoup(self.page,'lxml')
        else:
            raise CommunicationInterruptions(self.url)

        self.host = util.get_domain(self.url)

    def get_episode_link(self,episode_info):
        page = util.get(episode_info['link'])
        soup = BeautifulSoup(page,'lxml')
        script = soup.find('script',{'type':'text/javascript'}).text.replace('return p','console.log(p)')
        self.script_tool = ScriptTool()
        result = self.script_tool.run_script(script.encode('UTF-8').strip().split('\n')[2])
        urls = result.replace('var pages=pages=\'','').replace('"}\';','"}').replace("]';",'').replace('["','"').replace('"','').replace('\/','/').split(',')
        for i in range(0,len(urls)):
            urls[i] = 'http://images.dmzj.com/' + urls[i]

        return urls

    def get_picture(self,url):
        return util.get(url,header={
                                    'Referer':'http://www.dmzj.com/',
                                    'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36'
                                        }
                            )

    def get_comic_name(self):
        #g_comic_name = "一拳超人";
        return re.findall('g_comic_name = "(.*?)";',self.page)[0]

    def get_cover(self):
        element = self.bs.findAll('img',{'id':'cover_pic'})[0]
        return util.get(element['src'],header = {'Referer':self.url})

    def get_index(self):#<div class="cartoon_online_border" >
        element = self.bs.findAll('div',{'class':'cartoon_online_border'})[0]
        elements = element.findAll('li')
        episodes = []
        for li in elements:
            episodes.append(
                {
                    'link':self.host+li.a['href'][1:],
                    'title':li.a['title']
                    }
                )
        return episodes