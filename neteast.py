#coding:utf-8
#Alex

import urllib2
import re
import os
import sys
import getopt
import time
import json

re_test_url_index = 'http://manhua\.163\.com/source/[0-9]*'
re_get_manga_id = '"id": "([0-9]*?)",'
re_get_manga_title = 'book-title="(.*?)"'

el_tag = {
    'I':'[Info]',
    'W':'[Warning]',
    'E':'[Error]',
    'D':'[Debug]',
    'F':'[Fail]'
    }
cl = '['
cr = ']'
el_joiner = ': '
el_separator = ' '
el_newline = '\n'

def easy_log(content,level = 'I',time_format = '%H:%M:%S',std = sys.stdout,separator = el_separator):
    ftag=el_tag.get(level,level)
    if time_format=='%H:%M:%S':
        std.write(''.join([cl,time.strftime(time_format,time.localtime(time.time())),cr,separator,ftag,el_joiner,content,el_newline]))
    else:
        try:
            std.write(''.join([cl,time.strftime(time_format,time.localtime(time.time())),cr,separator,ftag,el_joiner,content,el_newline]))
        except:
            std.write(''.join([cl,time.strftime('%H:%M:%S',time.localtime(time.time())),cr,separator,ftag,el_joiner,content,el_newline]))
    return True

def creat_folder(path):
    path = path.replace('\\',os.sep)
    path = path.replace('/',os.sep)
    if path.find(os.sep)==-1:
        if not os.path.exists(path):
            os.mkdir(path)
    else:
        path=path.split(os.sep)
        path0=''
        for path_item in path:
            path0=path0+path_item+os.sep
            if not os.path.exists(path0):
                os.mkdir(path0)

def string_test(url):
    if len(re.findall(re_url_index,url))>0:
        return True
    return False

def get(url,max_try = 8,flag_exit=False):
    try_count = max_try
    while try_count:
        try:
            respon = urllib2.urlopen(url)
            return respon.read()
        except:
            easy_log('Can\'t reach url: '+url+'., try[%s/%s].' % (max_try-try_count+1,max_try,),std=sys.stderr,level = 'E')
        try_count-=1
    easy_log('Can\'t reach url: '+url+'. Max try.',std=sys.stderr,level = 'E')
    if flag_exit:
        exit(-1)

def main(url,path):
    index_page = get(url,flag_exit = True)
    manga_id = re.findall(re_get_manga_id,index_page)[0]
    manga_title = re.findall(re_get_manga_title,index_page)[0]
    episodes_json = get('http://manhua.163.com/reader/bookInfo/'+str(manga_id),flag_exit = True)
    episodes = json.loads(episodes_json)
    sections = episodes['sections'][0]['sections']
    count_sections = len(sections)
    count_loop = 1
    for section in sections:
        easy_log('Downloading episode %s/%s ...' % (count_loop,count_sections,),std=sys.stdout,level = 'I')
        order = section['titleOrder']
        text = section['titleText']
        if 'fakeChapter' in [order,text]:
            continue
        creat_folder(path+os.sep+str(section_id)+'_'+order.replace(' ','')+'_'+text)
        section_id = section['sectionId']
        picture_json = get('http://manhua.163.com/reader/section/%s/%s' % (manga_id,section_id),flag_exit = True)
        pictures = json.loads(picture_json)
        pictures_info = pictures['images']
        for picture in pictures_info:
            picture_data = get(picture['url'])
            picture_name = picture['title']+'.'+picture['imageType']
            f = open(path+os.sep+order+'_'+text+os.sep+picture_name,'wb')
            f.write(picture_data)
            f.close()
        count_loop+=1





if __name__=='__main__':
    path = '.'
    url = ''
    if len(sys.argv)<=1:
        easy_log('Please enter the url of the manga.',std=sys.stderr,level = 'E')
        exit(-1)
    else:
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'p:')
        except:
            easy_log('Unknow option(s).',std=sys.stderr,level = 'E')
            exit(-1)
        if len(args)==0:
            easy_log('Please enter the url of the manga.',std=sys.stderr,level = 'E')
            exit(-1)
        else:
            for a_url in args:
                if len(re.findall(re_test_url_index,a_url))!=0:
                    url = a_url
                    break
                else:
                    pass
            if url=='':
                easy_log('Please enter the url of the manga.',std=sys.stderr,level = 'E')
                exit(-1)
        for op, value in opts:
            if op == '-p':
                path = value
            else:
                pass
    main(url,path)