# -*- coding: utf-8 -*-

import sys
import json
import time
import shutil
import getopt
from prettytable import PrettyTable

import libs.util as util
from libs.core import *

#plugin = util.plugin_loader('plugin'+os.sep+'export')
#exports = util.loader_in_main(plugin,'Source')

TIME_FROMAT = '%Y%m%d%H%M%S'

plugins = []
tests = []

def init():
    global tests
    global plugins
    
    util.easy_log('Loading source plugins...')
    plugins = util.plugin_loader('plugin'+os.sep+'sources')
    plugins = util.loader_in_main(plugins,'Source')

    util.easy_log('Preparing file-system...')
    util.creat_folder('_database')
    util.creat_folder('_database'+os.sep+'index')
    util.creat_folder('_database'+os.sep+'pictures')

    
    util.easy_log('Loading tester from plugins...')
    for plugin in plugins:
        tests.append(plugin.test)

def list_sources():
    try:
        f = open('_database'+os.sep+'sources.json','rb')
        table = PrettyTable(['Plugin','Credential','Url','Name'])
        for line in json.loads(f.read()):
            table.add_row([line['plugin'],line['credential'],line['url'],line['name']])
        print 
        print str(table).decode('UTF-8')
    except:
        util.easy_log('No sources file found.')

def reflection(key):
    if util.is_url(key):
        for test in tests:
            if test(key):
                for plugin in plugins:
                    if plugin.name()==test(key):
                        return plugin
                    else:
                        continue
            else:
                continue
        return False
    else:
        for plugin in plugins:
            if plugin.name()==key:
                return plugin
            else:
                continue
        return False

def diff(info):
    pass 

def sync(info):
    util.easy_log('Try to sync data for '+info['name'].decode('UTF-8')+'...')
    plugin = reflection(info['plugin'])
    object_ = plugin(info['url'])
    urls = object_.get_index()
    date = time.strftime(TIME_FROMAT, time.localtime(time.time()))
    json_object = {
        'episodes':urls,
        'time':date
    }
    json_string = json.dumps(json_object)
    file_name = info['plugin']+'_'+info['credential']
    if os.path.isfile('_database'+os.sep+'index'+os.sep+file_name+'.json'):
        util.easy_log('Do not turn off your system during the saving. Interrupting the installation can cause your system to be damaged.')
        try:
            os.remove('_database'+os.sep+'index'+os.sep+file_name+'_old.json')
        except:
            pass    
        shutil.move('_database'+os.sep+'index'+os.sep+file_name+'.json','_database'+os.sep+'index'+os.sep+file_name+'_old.json')
        file_handle = open('_database'+os.sep+'index'+os.sep+file_name+'.json','wb')
        file_handle.write(json_string)
        file_handle.close()
    else:
        util.easy_log('Do not turn off your system during the saving. Interrupting the installation can cause your system to be damaged.')
        file_handle = open('_database'+os.sep+'index'+os.sep+file_name+'.json','wb')
        file_handle.write(json_string)
        file_handle.close()
    util.easy_log('Sync finished.')

def search(plugin = None,credential = None):
    to_return = []
    mid = []
    if plugin==None and credential==None:
        util.easy_log('No rules.','I')
    else:
        try:
            f = open('_database'+os.sep+'sources.json','rb')
            json_ = json.loads(f.read())
            f.close()
        except:
            util.easy_log('No sources data.','D')
            exit(-1)
        for info in json_:
            if info['plugin'] == plugin:
                mid.append(info)
        for info in mid:
            if info['credential'] == credential:
                to_return.append(info)
        return to_return

def add(url,class_):
    util.easy_log('Load plugin '+class_.version()+'...')
    object_ = class_(url)
    util.easy_log('Url: '+object_.url+'...')
    util.easy_log('Comic name: '+object_.get_comic_name().decode('UTF-8')+'...')
    util.easy_log('Add new item to database...')
    credential = object_.credential
    url = object_.url
    try:
        f = open('_database'+os.sep+'sources.json','rb')
        json_ = json.loads(f.read())
        f.close()
        f = open('_database'+os.sep+'sources.json','wb')
    except:
        f = open('_database'+os.sep+'sources.json','wb')
        json_ = []
    info = {
                'plugin':object_.name(),
                'credential':credential,
                'url':url,
                'name':object_.get_comic_name(),
                'sync':0
                }
    json_.append(info)
    sync(info)
    json_[-1]['sync'] = time.strftime(TIME_FROMAT, time.localtime(time.time()))
    f.write(json.dumps(json_))
    f.close()
    exit(0)

def down(info):
    if not info['sync']:
        util.easy_log('Never sync.Please use \'unname -s\' to sync it.')
    else:
        util.easy_log('Last sync '+info['sync']+'.')
    plugin = reflection(info['plugin'])
    object_ = plugin(info['url'])
    try:
        file_name = info['plugin']+'_'+info['credential']
        file_handle = open('_database'+os.sep+'index'+os.sep+file_name+'.json','rb')
        json_ = json.loads(file_handle.read())
        episodes = json_['episodes']
        pictures_info = {}
        for episode in episodes:
            util.easy_log('Downloading episode '+episode['title']+'...')
            pictures_info[episode['title']]={}
            for a_link in object_.get_episode_link(episode):
                picture_raw = object_.get_picture(a_link)
                pictures_info[episode['title']][a_link] = '_database'+os.sep+'pictures'+os.sep+a_link.replace('/','_')
                f = open('_database'+os.sep+'pictures'+os.sep+a_link.replace('/','_').replace(':','_').replace('\n',''),'wb')
                f.write(picture_raw)
                f.close()#dmzj_jp_yiquanchaoren
        file_name = info['plugin']+'_'+info['credential']+'_files.json'
        f = open('_database'+os.sep+'index'+os.sep+file_name,'wb')
        f.write(json.dumps(pictures_info))
        f.close()
    except:
        util.easy_log('An error occoued when down pictures.')




if __name__=='__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ld:a:s:')
    except:
        util.easy_log('Invalid parameter.','F')
        exit(1)
    init()
    for op, value in opts:
        if op == '-l':
            list_sources()
        elif op == '-a':
            url = value
            class_ = None
            for test in tests:
                t = test(url)
                if t:
                    class_ = reflection(t)
                else:
                    continue
            if class_:
                add(url,class_)
            else:
                util.easy_log('No plugin can deal with url \''+url+'\'.','D')
                #record inv url
                exit(1)
        elif op == '-s':
            credential = value
            if credential:
                if util.is_url(credential):
                    for test in tests:
                        if test(credential):
                            plugin = reflection(credential)
                            object_ = plugin(credential)
                            info = {
                                        'plugin':object_.name(),
                                        'credential':object_.credential,
                                        'url':credential,
                                        'name':object_.get_comic_name()
                                        }
                            result = search(info['plugin'],info['credential'])
                            if result==[]:
                                util.easy_log('Can\'t find item.Please use \'unname -a\' to add it.')
                            else:
                                sync(result[0])
                        else:
                            util.easy_log('No plugin can deal with url \''+url+'\'.','D')
                            #record inv url
                            exit(1)
                else:
                    result = search(None,credential)
                    sync(result[0])
        elif op == '-d':
            credential = value
            if credential:
                if util.is_url(credential):
                    for test in tests:
                        if test(credential):
                            plugin = reflection(credential)
                            object_ = plugin(credential)
                            info = {
                                        'plugin':object_.name(),
                                        'credential':object_.credential,
                                        'url':credential,
                                        'name':object_.get_comic_name()
                                        }
                            result = search(info['plugin'],info['credential'])
                            if result==[]:
                                util.easy_log('Can\'t find item. Please use \'unname -a\' to add it.')
                            else:
                                if result[0]['sync']:
                                    down(result[0])
                                else:
                                    util.easy_log('Never sync. Please use \'unname -s\' to sync it.')
                        else:
                            util.easy_log('No plugin can deal with url \''+url+'\'.','D')
                            #record inv url
                            exit(1)
                else:
                    result = search(None,credential)
                    if result==[]:
                        util.easy_log('Can\'t find item. Please use \'unname -a\' to add it.')
                    else:
                        if result[0]['sync']:
                            down(result[0])
                        else:
                            util.easy_log('Never sync. Please use \'unname -s\' to sync it.')