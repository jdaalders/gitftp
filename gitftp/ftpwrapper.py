"""FTP wrapper"""
import os
from ftplib import FTP, error_perm
from colorama import Fore, init
init()


class FtpWrapper(object):
    """FTP Wrapper class"""

    def __init__(self, host, rootdir, username, password):
        """Initialize"""
        self.root_dir = rootdir
        self.connect_ftp(host, username, password)

    def __del__(self):
        """Destructor"""
        if self.ftp != None:
            self.ftp.quit()

    def connect_ftp(self, host, username, password):
        """Make FTP connection"""
        self.ftp = FTP(host)
        self.ftp.login(username, password)
        self.set_root_dir()

    # def connect_sftp(self, host, rootdir, username, password):
    #     """Make Secure FTP connection"""
    #     print("SFTP not supported")

    def set_root_dir(self):
        """Set root directory on the server"""
        self.ftp.cwd('/'+self.root_dir)

    def upload(self, localpath, path):
        """Upload file to the server"""
        self.set_root_dir()

        print(Fore.CYAN + "Upload file: " + path + Fore.RESET)
        (filepath, filename) = os.path.split(path)

        # open file path
        self.open_remote_file_path(filepath)

        # check if file exists on the local machine
        realpath = os.path.join(os.getcwd(), localpath)
        # upload the file
        if os.path.isfile(realpath):
            self.ftp.storbinary('STOR '+filename, open(realpath, 'r+b'))

        print("File: '" + path + "' uploaded " + Fore.GREEN + "successfully")
        print(Fore.RESET)

    def delete(self, path):
        """Delete file on the server"""
        self.set_root_dir()

        (filepath, filename) = os.path.split(path)

        # open file path
        self.open_remote_file_path(filepath)

        try:
            print(Fore.BLUE + "Delete file: " + path + Fore.RESET)
            self.ftp.delete(filename)
            print("File: '" + path + "' deleted " + Fore.GREEN + "successfully")
            print(Fore.RESET)

        except error_perm:
            print(Fore.RED + "File does not exists on the server")
            print(Fore.RESET)

        # remove empty directories
        self.remove_empty_directories(filepath)



    def open_remote_file_path(self, filepath):
        """Open file path on the server and create non-existing directories"""
        if filepath != "":
            filepathlist = filepath.split('/')

            for directory in filepathlist:
                # verify if directory exists
                exists = self.check_if_directory_exists(directory)

                # create directory on the server
                if not exists:
                    self.ftp.mkd(directory)

                # Set the current directory on the server.
                self.ftp.cwd(directory)

    def check_if_directory_exists(self, directory):
        """Check if directory exists"""
        directories = self.get_current_dir_subdirs()
        return directory in directories

    def get_current_dir_subdirs(self):
        """Get sub-directories from current directory"""
        ret = []
        self.ftp.dir("", ret.append)
        ret = [x.split()[-1] for x in ret if x.startswith("d")]
        return ret

    def is_current_directory_empty(self):
        """Check if current directory is empty"""
        ret = []
        self.ftp.dir("", ret.append)

        if len(ret) == 0:
            return True

        return False

    def remove_empty_directories(self, filepath):
        """Remove empty directories"""
        self.set_root_dir()
        if filepath != '':
            filepathlist = filepath.split('/')

            for directory in filepathlist:
                # Set the current directory on the server.
                self.ftp.cwd(directory)

                # check if current dir is emtpy
                dir_emtpy = self.is_current_directory_empty()

                if dir_emtpy:
                    # remove current dir
                    self.ftp.rmd('.')
