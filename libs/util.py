import re
import os
import sys
import time
import urllib2
import platform
import subprocess

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
    if ftag in ['E','F']:
        std = sys.stderr
    try:
        try:
            std.write(''.join([cl,time.strftime(time_format,time.localtime(time.time())),cr,separator,ftag,el_joiner,content,el_newline]))
        except:
            std.write(''.join([cl,time.strftime(time_format,time.localtime(time.time())),cr,separator,ftag,el_joiner,content.encode('UTF-8'),el_newline]))
    except:
        try:
            std.write(''.join([cl,time.strftime('%H:%M:%S',time.localtime(time.time())),cr,separator,ftag,el_joiner,content,el_newline]))
        except:
            std.write(''.join([cl,time.strftime('%H:%M:%S',time.localtime(time.time())),cr,separator,ftag,el_joiner,content.encode('UTF-8'),el_newline]))
    return True

def file_name_filer(string,replacment=''):
    list_=['/','\\','*',':','?','"','<','>','|']
    new=''
    for i in string:
        if i not in list_:
            new+=i
        else:
            new+=string,replacment
    return new

def get(url,header = {},max_try = 8,flag_exit = False):
    try_count = max_try
    if header == {}:
        while try_count:
            try:
                respon = urllib2.urlopen(url)
                return respon.read()
            except:
                easy_log('Can\'t reach url: '+url+', try[%s/%s].' % (max_try-try_count+1,max_try,),std=sys.stderr,level = 'E')
            try_count-=1
    else:
        request = urllib2.Request(url)
        for key in header:
            request.add_header(key,header[key])
        while try_count:
            try:
                respon = urllib2.urlopen(request)
                return respon.read()
            except:
                easy_log('Can\'t reach url: '+url+', try[%s/%s].' % (max_try-try_count+1,max_try,),std=sys.stderr,level = 'E')
            try_count-=1
    easy_log('Can\'t reach url: '+url+'. Max try.',std=sys.stderr,level = 'E')
    if flag_exit:
        exit(-1)

def url_completion(url,default='http'):
    url_part = url[:8]
    if url[:7]=='http://' or url_part=='https://':
        return url
    else:
        pass
    if url_part.find('s:')!=-1:
        to_add = 'http'
        while to_add!='':
            to_return = to_add+url
            if to_return[:7]!='https:/':
                to_add=to_add[:-1]
                continue
            else:
                return to_return
    elif url_part.find('p:')!=-1:
        to_add = 'htt'
        while to_add!='':
            to_return = to_add+url
            if to_return[:7]!='http://':
                to_add=to_add[:-1]
                continue
            else:
                return to_return
    else:
        to_add = 'http://'
        while to_add!='':
            to_return = to_add+url
            if to_return[:7]!='http://':
                to_add=to_add[:-1]
                continue
            else:
                while to_return.find('///')!=-1:
                    to_return = to_return.replace('///','//')
                return to_return
            to_add=to_add[:-1]

def get_domain(url):
    url = url_completion(url)+'/'
    return re.findall('((http|https|)://.*?/)',url)[0][0]

def get_temp_folder():
    platform_ = platform.system()
    if platform_=='Windows':
        return subprocess.check_output('echo %temp%',shell=True).replace('\r\n','')
    elif platform_=='Linux':
        return '/tmp'
    elif platform_=='OSX?':
        return '.'
    else:
        return None

def plugin_loader(folder,):
    dir_list = os.listdir(folder)
    plugins = {'object':'','names':[]}
    for dir_ in dir_list:
        if dir_.split('.')[-1]=='py' and dir_[:2]!='__':
            plugins['object'] = __import__(folder.replace(os.sep,'.')+'.'+dir_.split('.')[0])
            plugins['names'].append(folder.replace(os.sep,'.')+'.'+dir_.split('.')[0])
    return plugins

def loader_in_main(plugins,class_name):
    main_name = plugins['object'].__name__
    classes = []
    for name in plugins['names']:
        classes.append(eval('plugins[\'object\']'+name[len(main_name):]+'.'+class_name))
    return classes

def is_url(string):
    try:
        re_ = re.findall('((http|https)://.*)',string)[0]
    except:
        return False
    if len(re_)>1:
        return True
    else:
        return False

def creat_folder(path):
    path=path.replace('/',os.sep).replace('\\',os.sep)
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

def un(list_):
  new = []
  for i in list_:
    if type(i)==list:
      new+=un(i)
    else:
      new+=[i]
  return new