"""Git ftp module"""
import sys
import pygit2
from colorama import Fore, init
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from gitftp import GitWrapper

VERSION = "1.0.1"

try:
    repo = pygit2.Repository('.')
except:
    print("No repository found.")
    sys.exit(0)


def main(argv):
    """Define commands"""
    try:
        command = argv[0]
    except IndexError:
        print(Fore.RED + 'No arguments specified. Use "git ftp add <server>" or "git ftp deploy"')
        sys.exit(0)

    if command == 'add': # git ftp add <name> <url> (e.g.: git ftp add production ftp://example.com)
        ftpname = get_ftp_name(argv)
        wrapper = GitWrapper(repo)
        wrapper.add_server(ftpname, argv[2:])

    if command == 'deploy':
        try:
            ftpname = argv[1]
        except IndexError:
            ftpname = None

        wrapper = GitWrapper(repo)
        wrapper.deploy(ftpname)

    if command == 'remove':
        try:
            ftpname = argv[1]
        except IndexError:
            ftpname = None

        wrapper = GitWrapper(repo)
        wrapper.remove(ftpname)

    if command == 'servers':
        wrapper = GitWrapper(repo)
        wrapper.servers()

    if command == '-v':
        print("GitFTP version: '" + str(VERSION) + "'")



def get_ftp_name(argv):
    """Get ftp name from arguments"""
    try:
        ftpname = argv[1]
        return ftpname
    except:
        print(Fore.RED + 'specify a name for the ftp server.')
        print('e.g.: git ftp add production ftp://example.com')
        print(Fore.RESET)
        sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
