# -*- coding: utf-8 *-*

# imports
import os
import multiprocessing
import threading
import configparser
import sys
import traceback
import time
from pathlib import Path
import source.process as process

debug_mode = False
ftp_connections = {}
cores = 1
repos = []

try:
    #detect os for know worker_directory
    if sys.platform == 'win32':
        os_path = 'C:\Deploy\prepare-to-ftp\\'
        if not os.path.isdir(os_path):
            os.makedirs(os_path)
    else:
        os_path = str(Path.home()) + '\.prepare-to-ftp'

    #define worker_directory
    process.os_path = os_path

    # configparser for get configurations
    cur_path = os.path.dirname(os.path.abspath(__file__))

    config = configparser.ConfigParser()
    config.read(cur_path + '/configs/config.ini')

    #diccionary with connections
    for con in config['ftp_connections']:
        ftp_connections[con] = config['ftp_connections'][con]
    
    #create all repo_objects 
    for repo in config['repos']:
        connectionName = config[ftp_connections.get(
            config[repo]['ftp_connection'])]
        repos.append(process.repositori(
            repo, config['repos'][repo], config[repo], connectionName))
    
    #loop for check reporitory changes
    if True:
        for run_repo in repos:
            p = None
            p = threading.Thread(target=run_repo.run)
            p.start()
        time.sleep(5)#timeOut 

except Exception as e:
    if debug_mode:
        print(traceback.format_exc())
    print("\n\nSorry the configuration is bad please read the confiuration in the file README.md or is a problem with the code please report franevarez@gmail.com\n")
