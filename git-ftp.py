import sys
import getpass
import pygit2
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from gitftp import GitWrapper

try:
	repo = pygit2.Repository('.')
except:
    print("No repository found.")
    sys.exit(0)


def main(argv):
	command = argv[0]

	if command == 'add': # git ftp add <name> <url> (e.g.: git ftp add production ftp://example.com)
		ftpname = getFTPName(argv)
		f = GitWrapper(repo, ftpname)
		f.add_server(argv[2:])

	if command == 'deploy':
		ftpname = getFTPName(argv)
		f = GitWrapper(repo, ftpname)
		f.deploy()



def getFTPName(argv):
	# get ftp name
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
