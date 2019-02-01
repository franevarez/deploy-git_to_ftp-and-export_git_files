# -*- coding: utf-8 *-*

import os
import sys
import git
from ftplib import FTP

os_path = ''

#principal object for repo objects
class repositori():
    def __init__(self, name, git_rute, configs, connection):
        #add all configuration that need
        self.name = name
        self.git_rute = git_rute
        self.branch = configs['branch']
        self.ftp_rute = configs['ftp_rute']
        self.ftp_connection = configs['ftp_connection']
        self.original_rutes = configs['original_rutes'].split(sep='\n')
        self.new_rutes = configs['new_rutes'].split(sep='\n')
        self.connection_settings = connection

    #function fer check and get remote changes
    def get_git(self):
        is_repo_new = False
        if not os.path.isdir(os_path + self.name):
            git.Git(os_path).clone(self.git_rute)
            is_repo_new = True

        repo = git.Repo(os_path +self.name)

        repo.git.checkout('des')
        repo.remotes.origin.fetch()

        changes = len(list(repo.iter_commits('origin/des'))) - \
            len(list(repo.iter_commits('des')))

        if changes > 0 or is_repo_new:

            repo.git.pull('--all')
            
            if is_repo_new:
                files_modified = list(repo.git.ls_files().split(sep='\n'))

            else:
                files_modified = list(repo.git.log(
                    '-{}'.format(changes), '--name-only', "--pretty=format:''").split(sep='\n'))

            while "''" in files_modified:
                files_modified.remove("''")

            while '' in files_modified:
                files_modified.remove('')

            files_correct = []

            for list_f in files_modified:
                add = False

                for rute_old, rute_new in zip(self.original_rutes, self.new_rutes):
                    
                    if rute_old in list_f:
                        name_file = list_f[len(rute_old):] 
                        print(name_file)

                        files_correct.append(rute_new+name_file)
                        add = True

                if not add:
                    files_correct.append(list_f)

            print(files_modified)
            print(files_correct)
            
            self.list_local_files = files_modified
            self.list_remote_files = files_correct
        
            return True
        else:
            return False

    #function for send all files to ftp rute configurate
    def send_ftp(self):

        ftp = FTP(self.connection_settings['server'])
        ftp.login(self.connection_settings['user'], self.connection_settings['password'])

        for local, remote in zip(self.list_local_files, self.list_remote_files):
            print(os_path + self.name + '\\' + local.replace('/', '\\'))

            ftp_upload(os_path + self.name + '\\' + local.replace('/', '\\'), self.ftp_rute + remote, ftp)

        ftp.cwd(self.ftp_rute)
        ftp.retrlines('LIST')
        
        ftp.quit()

    #Start function for the objects repositori
    def run(self):
        print("Scann")
        if self.get_git():
            self.send_ftp()

#function to upload a file
def ftp_upload(localfile, remotefile, ftp):
    print("ftp_upload: ",localfile, remotefile, ftp)
    fp = open(localfile, 'rb')
    try:
        ftp.storbinary('STOR %s' % remotefile, fp, 1024)
    except Exception:
        print("remotefile not exist error caught" + remotefile)
        path, filename = os.path.split(remotefile)

        path_list = path.split(sep='/')

        if "" in path_list:
                path_list.remove("")

        #define path for add folders and scan if existing   
        path = '/'

        #loop for scanning if necesary directory exists
        for folder in path_list:
            if not directory_exists(path, folder, ftp):
                ftp.cwd(path)
                ftp.mkd(folder)
            path = path + folder + '/'

        print("creating directory: " + remotefile)
        ftp_upload(localfile, remotefile, ftp)
        return
    print ("after upload " + localfile + " to " + remotefile)

#chech if directory exist in the ftp server
def directory_exists(dir, folder, ftp):
    print(folder)
    filelist = []
    ftp.cwd(dir)
    ftp.retrlines('LIST', filelist.append)
    for f in filelist:
        if f.split()[-1] == folder and f.upper().startswith('D'):
            print('Exists', folder)
            return True
    print('No Exists', folder)
    return False
    
