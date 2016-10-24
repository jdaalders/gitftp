"""GIT wrapper"""
import sys
import getpass
from enum import IntEnum
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from colorama import Fore, init
from .ftpwrapper import FtpWrapper
from .gitconfig import GitConfig
init()


class DiffFile(IntEnum):
    """Diff file status"""
    added = 1
    deleted = 2
    changed = 3

class GitWrapper:
    """GitWrapper class"""
    latest = '/'
    ftpwrapper = None

    def __init__(self, repo, ftpname):
        """Initialize"""
        self.repo = repo

        if ftpname != None:
            self.ftpname = ftpname
            self.gitconfig = GitConfig(self.repo)

            self.type = self.gitconfig.get('ftp.' + str(ftpname) + '.type')
            self.host = self.gitconfig.get('ftp.' + str(ftpname) + '.host')
            self.username = self.gitconfig.get('ftp.' + str(ftpname) + '.username')
            self.password = self.gitconfig.get('ftp.' + str(ftpname) + '.password')
            self.localdir = self.gitconfig.get('ftp.' + str(ftpname) + '.localdir')
            self.remotedir = self.gitconfig.get('ftp.' + str(ftpname) + '.remotedir')
            self.latest = self.gitconfig.get('ftp.' + str(ftpname) + '.latest')


    def add_server(self, argv):
        """add ftp server"""
        print(Fore.YELLOW + 'FTP; add server settings' + Fore.RESET)

        # get ftp url
        try:
            ftpurl = argv[0]
        except:
            print(Fore.RED + 'specify an url for the ftp server.')
            print('e.g.: git ftp add production ftp://example.com')
            print(Fore.RESET)
            return None

        # add ftp server information
        username = input('username: ')
        pswd = getpass.getpass('Password:')

        # set localdir input string
        localdir_input_str = 'local directory'
        if self.localdir is None:
            localdir_input_str += ': '
        else:
            localdir_input_str += ' (' + self.localdir + ')'

        localdir = input(localdir_input_str)
        if localdir == '':
            localdir = self.localdir

        # set remotedir input string
        remotedir_input_str = 'remote directory'
        if self.remotedir is None:
            remotedir_input_str += ': '
        else:
            remotedir_input_str += ' (' + self.remotedir + ')'

        remotedir = input(remotedir_input_str)
        if remotedir == '':
            remotedir = self.remotedir

        self.gitconfig.set('ftp.' + str(self.ftpname) + '.type', 'ftp')
        self.gitconfig.set('ftp.' + str(self.ftpname) + '.host', str(ftpurl))
        self.gitconfig.set('ftp.' + str(self.ftpname) + '.username', str(username))
        self.gitconfig.set('ftp.' + str(self.ftpname) + '.password', str(pswd))
        self.gitconfig.set('ftp.' + str(self.ftpname) + '.localdir', str(localdir))
        self.gitconfig.set('ftp.' + str(self.ftpname) + '.remotedir', str(remotedir))

        print(Fore.GREEN + "FTP server '" + str(self.ftpname) + "' added." + Fore.RESET)

    def deploy(self):
        """Deploy changes"""
        print(Fore.YELLOW + 'FTP; deploy to server' + Fore.RESET)

        sexists = self.server_exists(self.ftpname)
        if not sexists:
            print(Fore.RED + 'Server does not exists' + Fore.RESET)
            return None

        # get latest sync hash from config
        try:
            latest_sync_hash = self.gitconfig.get('ftp.' + str(self.ftpname) + '.latest')
			    # self.repo.config.get_multivar('ftp.' + str(self.ftpname) + '.latest', None).next()
        except:
            latest_sync_hash = ""

        # count how much you are behind with syncing
        sync_behind_count = self.find_sync_offset(latest_sync_hash)
        if sync_behind_count == 0:
            print(Fore.GREEN + "Already up to date!")
            return None
        elif sync_behind_count == 1:
            self.sync_latest_commit()
        elif sync_behind_count > 1:
            self.make_sync_choice(sync_behind_count, latest_sync_hash)

    def make_sync_choice(self, sync_behind_count, latest_sync_hash):
        """Make sync choice"""
        print(Fore.CYAN + "You're " + str(sync_behind_count) +\
            " commits behind. What would you like to do:" + Fore.RESET)
        print("1) catchup")
        print("2) sync only latest")
        print("3) choose commits to sync")
        choice = input('make a choice (1): ')
        print("")

        # set default to '1' when nothing is pressed
        if choice == "":
            choice = 1

        if str(choice) == '1':                                    # catchup
            self.catchup_commits(latest_sync_hash)
        elif str(choice) == '2':                                  # sync only latest
            self.sync_latest_commit()
        elif str(choice) == '3':                                  # choose commits to sync
            self.cherry_pick_commit(latest_sync_hash)
        else:
            print(Fore.RED + 'Unknown choice.' + Fore.RESET)
            return None


    def find_sync_offset(self, latest_sync_hash):
        """Find offset"""
        commit_count = 0
        for commit in self.repo.walk(self.repo.head.target, GIT_SORT_TOPOLOGICAL):
            if str(commit.id) == str(latest_sync_hash):
                return commit_count
            else:
                commit_count += 1
                continue

        return commit_count

    def catchup_commits(self, latest_sync_hash):
        """Catchup commit to the latest"""
        print(Fore.YELLOW + "Catching up all commits" + Fore.RESET)

        # get current commit (head)
        head = self.repo.head
        latest_commit = head.get_object()

        # get latest synced commit
        if latest_sync_hash == '':
            for commit in self.repo.walk(self.repo.head.target,\
			  GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
                latest_synced_commit = self.repo.get(commit.id)
                break
        else:
            latest_synced_commit = self.repo.get(latest_sync_hash)

        # process diff files
        self.process_diff_files(latest_synced_commit, latest_commit)

        # update latest commit hash
        print(Fore.GREEN + "FTP catched up with latest commit: " +\
		  str(latest_commit.id) + Fore.RESET)
        self.set_latest_sync_hash(self.latest, latest_commit.id)

    def sync_latest_commit(self):
        """Sync only the latest commit"""
        print(Fore.YELLOW + "Sync latest commit" + Fore.RESET)

        head = self.repo.head
        latest_commit = head.get_object()

        # get parent from commit
        parent = self.find_parent_from_commit(latest_commit)

        # process diff files
        self.process_diff_files(parent, latest_commit)

        # update latest commit hash
        print(Fore.GREEN + "FTP synced with latest commit: " + str(latest_commit.id) + Fore.RESET)
        self.set_latest_sync_hash(self.latest, latest_commit.id)

    def cherry_pick_commit(self, latest_sync_hash):
        """Cherry pick commits to sync"""
        print(Fore.YELLOW + "Choose commits to sync" + Fore.RESET)

        start = False
        if latest_sync_hash == '':
            start = True

        for commit in self.repo.walk(self.repo.head.target,\
		  GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
            # find start point
            if not start:
                if str(commit.id) == str(latest_sync_hash):
                    start = True
                continue

            # start syncing
            print(Fore.CYAN + str(commit.id) + Fore.RESET + " - " + Fore.GREEN +\
			  "(" + str(commit.committer.offset) + ")" + Fore.RESET + " " + commit.message.replace('\n', ' ').replace('\r', '').strip() + Fore.MAGENTA + " - " + str(commit.committer.name) + Fore.RESET) # str(commit.committer.name)


            sync_commit = input('Do you want to sync this commit? (Y): ')
            if sync_commit == "y" or sync_commit == "Y" or sync_commit == "":
                # process diff
                parent = self.find_parent_from_commit(commit)
                self.process_diff_files(parent, commit)

                # set latest hash
                self.set_latest_sync_hash(self.latest, commit.id)
            else:
                print("Commit skipped")

            print(Fore.RESET)

    def find_parent_from_commit(self, commit):
        """Find parent commit"""
        parent = None
        if len(commit.parent_ids) > 0:
            for parent_id in commit.parent_ids:
                # get parent commit
                parent = self.repo.get(parent_id)

        return parent

    def process_diff_files(self, parent, commit):
        """Process diff"""
        self.ftpwrapper = FtpWrapper(self.host, self.remotedir, self.username, self.password)

        if parent is None:
            #get diff for commit
            commit_diff = commit.tree.diff_to_tree(swap=True)
        else:
            #get diff between a and b
            commit_diff = self.repo.diff(parent.tree, commit.tree)

        for diff in commit_diff.__iter__():
            # get delta
            delta = diff.delta

            process = False
            remote_file_name = delta.new_file.path
            if self.localdir != '':
                process = delta.new_file.path.startswith(self.localdir, 0, len(self.localdir))
                remote_file_name = remote_file_name.replace(self.localdir, '', 1)
                remote_file_name = remote_file_name.strip("/")
            else:
                process = True

            if process:
                if delta.status == DiffFile.added:            # file added
                    self.ftpwrapper.upload(delta.new_file.path, remote_file_name)
                elif delta.status == DiffFile.deleted:        # file deleted
                    self.ftpwrapper.delete(remote_file_name)
                elif delta.status == DiffFile.changed:        # file changed
                    self.ftpwrapper.upload(delta.new_file.path, remote_file_name)

    def server_exists(self, ftpname):
        """Server exists"""
        result = False
        try:
            server = self.gitconfig.get('ftp.' + str(ftpname) + '.type')
            if server != None:
                result = True
        except StopIteration:
            result = False

        return result

    def set_latest_sync_hash(self, replace, commithash):
        """Update hash"""
        try:
            print(replace)
            self.gitconfig.set('ftp.' + str(self.ftpname) + '.latest', str(commithash))
            self.latest = commithash
        except:
            print("error updating hash")
