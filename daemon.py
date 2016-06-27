# coding=gbk
'''
Created on 2016年1月17日

@author: 大雄
'''
import logging
import time
from tkinter import Tk
from tkinter.messagebox import askokcancel, CANCEL
import urllib.parse
import os

from utils import getHome, getConfig, checkUpdate, downloadFixPack, applyFixPack, \
    check_exsit


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')
    if check_exsit("fanUpdater.exe") > 1:
        logging.debug("another fanUpdater.exe exists")
        os._exit(2)
    
    config = getConfig("updater.ini")
    check_version_service = config.get("default", "check_version_service")
    fixpack_service = config.get("default", "fixpack_service")
    
    APP_HOME = getHome() + "/../"
    absolute_version_file      = APP_HOME + "properties/app.version"
    absolute_fixpack_file      = APP_HOME + urllib.parse.unquote(fixpack_service).split('/')[-1].split("?")[0]
    TEMP                       = getHome() + "/TEMP/"

    while True:
        version, md5 = checkUpdate(check_version_service, absolute_version_file)
        if version:
            root = Tk()
            root.withdraw()
            result = askokcancel("fanUpdater", "发现新版本，是否更新？",
                         default=CANCEL)
            print(result)
            root.destroy()
            if result:
                logging.debug("downloading...")
                if downloadFixPack(fixpack_service, absolute_fixpack_file, md5):
                    logging.debug("apply fix pack...")
                    applyFixPack(absolute_fixpack_file, APP_HOME, TEMP)
        #每隔10分钟检测一次最新更新
        time.sleep(600)