# coding=gbk
'''
Created on 2016年1月9日

@author: 大雄
'''
from configparser import ConfigParser
import hashlib
import logging
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
import win32com.client

def _checkUpdateVersion(service_url):
    new_version = None
    md5 = None
    try:
        response = urllib.request.urlopen(service_url, timeout=10)
        new_version, md5 = bytes.decode(response.read(),"utf8").split()
        logging.debug("version on the update server is: " + new_version)
    except Exception:
        logging.debug("check version fail")
        
    return new_version, md5

def _getLocalVersion(version_file):
    version = None
    f = None
    try:    
        f = open(version_file, "r", encoding="utf8")
        version = f.readline()
        logging.debug("local version: " + version)
    except Exception:
        logging.debug("local version can not found")
    finally:
        if f:
            f.close()
            
    return version

def downloadFixPack(url, filename, md5):
    path = os.path.dirname(filename) 
    if not os.path.exists(path):
        os.mkdir(path)
    urllib.request.urlretrieve(url, filename)
    return _md5check(md5, filename)

def applyFixPack(fixpack_file, app_home, temp):
    #clean temp dir
    if os.path.exists(temp):
        shutil.rmtree(temp)
    os.mkdir(temp)
    with zipfile.ZipFile(fixpack_file, 'r') as z:
        for f in z.namelist():
            path = os.path.join(temp, f)
            if path.endswith("/"):
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
            else:
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                with open(path, 'wb') as fp:
                    fp.write(z.read(f))
    
    for f in os.listdir(temp):
        path = temp + f
        if os.path.isdir(path):
            #shutil不支持覆盖
            #shutil.copytree(temp + f, app_home + f)
            cmd = """xcopy /S /Y /E /I "{0}" "{1}" """.format(temp + f, app_home + f)
            subprocess.call(cmd,shell=True)
        else:
            shutil.copyfile(path, app_home + f)
       
def _md5check(md5, filename):
    with open(filename, "r+b") as f:    
        m = hashlib.md5()
        m.update(f.read())
        new_md5 = m.hexdigest()
        logging.debug("file md5: " + new_md5)
    if not md5 and not new_md5:
        return True
    if not md5 or not new_md5:
        return False
    else:
        return new_md5 == md5  

def checkUpdate(check_version_service, absolute_version_file):
    #get new version and md5 for updates
    new_version, md5 = _checkUpdateVersion(check_version_service)
    local_version = _getLocalVersion(absolute_version_file)
    if not new_version:
        logging.debug("no new version can be found")
        return None, None
    if not local_version or local_version < new_version:
        logging.debug("new version found")
        return new_version, md5
    else:
        logging.debug("we have the lastest version")
        return None,None

def getConfig(conf):
    config = ConfigParser()
    config.read(getHome() + "/" + conf)
    return config

def getHome():
    p = sys.path[0]
    if os.path.isdir(p):
        return p
    elif os.path.isfile(p):
        return os.path.dirname(p)

def check_exsit(process_name):
    WMI = win32com.client.GetObject('winmgmts:')
    processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="%s"' % process_name)
    return len(processCodeCov)
