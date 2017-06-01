"""GIT wrapper"""
import getpass
from enum import IntEnum
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from colorama import Fore, init
from .ftpwrapper import FtpWrapper
from .ftpconfig import FtpConfig, ServerNotExist
from .githash import GitHash
init()


class EmptyList(Exception):
    pass


class DiffFile(IntEnum):
    """Diff file status"""
    added = 1
    deleted = 2
    changed = 3

class GitWrapper:
    """GitWrapper class"""
    ftpwrapper = None
    ftpname = None

    def __init__(self, repo):
        """Initialize"""
        self.repo = repo
        self.ftpconfig = FtpConfig()

    def load_configuration(self, section):
        """Load server configuration"""
        if section != None:
            self.ftpname = section

    def add_server(self, section, argv):
        """add ftp server"""
        print(Fore.YELLOW + 'FTP; add server settings' + Fore.RESET)
        self.load_configuration(section)

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
        section_localdir = self.ftpconfig.get_item(self.ftpname, 'localdir')
        if section_localdir is None:
            localdir_input_str += ': '
        else:
            localdir_input_str += ' (' + section_localdir + ')'

        localdir = input(localdir_input_str)
        if localdir == '':
            localdir = section_localdir

        # set remotedir input string
        remotedir_input_str = 'remote directory'
        section_remotedir = self.ftpconfig.get_item(self.ftpname, 'remotedir')
        if section_remotedir is None:
            remotedir_input_str += ': '
        else:
            remotedir_input_str += ' (' + section_remotedir + ')'

        remotedir = input(remotedir_input_str)
        if remotedir == '':
            remotedir = section_remotedir

        self.ftpconfig.set(self.ftpname, ftpurl, username, pswd, remotedir, localdir)
		
		# create hash file
        self.githash = GitHash(self.ftpname, localdir)

        print(Fore.GREEN + "FTP server '" + str(self.ftpname) + "' added." + Fore.RESET)

    def remove(self, section):
        if section is None:
            try:
                section = self.choice_section()
            except (ServerNotExist, EmptyList):
                return None

        if self.ftpconfig.remove_section(section):
            print(Fore.GREEN + "FTP server '" + section + "' removed successfully." + Fore.RESET)

    def servers(self):
        """List servers"""
        print(Fore.YELLOW + 'List of servers' + Fore.RESET)
        list = self.ftpconfig.list_sections()
        
        for idx, val in enumerate(list):
            print(val)
        

    def deploy(self, section):
        """Deploy changes"""
        print(Fore.YELLOW + 'FTP; deploy to server' + Fore.RESET)

        if section is None:
            try:
                section = self.choice_section()
            except (ServerNotExist, EmptyList):
                return None

        self.load_configuration(section)

        # check if configuration exists
        if self.ftpconfig.has_section(self.ftpname):
            # get latest sync hash from config
            try:
                localdir = self.ftpconfig.get_item(self.ftpname, 'localdir')
                githash = GitHash(self.ftpname, localdir)
                latest_sync_hash = githash.get()
            except Exception as error:
                latest_sync_hash = None

            # count how much you are behind with syncing
            sync_behind_count = self.find_sync_offset(latest_sync_hash)
            if sync_behind_count == 0:
                print(Fore.GREEN + "Already up to date!")
                return None
            elif sync_behind_count == 1:
                self.sync_latest_commit()
            elif sync_behind_count > 1:
                self.make_sync_choice(sync_behind_count, latest_sync_hash)
        else:
            print(Fore.RED + 'Server does not exists' + Fore.RESET)
            return None

    def choice_section(self):
        """Choose section"""
        list = self.ftpconfig.list_sections()

        if len(list) == 0:
            print(Fore.RED + 'Add a server before deploying!' + Fore.RESET)
            raise EmptyList()

        print(Fore.CYAN + 'Which configuration do you want to use?:' + Fore.RESET)

        for idx, val in enumerate(list):
            print(idx, val)

        use_section = input('section: ')
        try:
            index = int(use_section)
            section = list[index]
            print("")
            return section
        except (ValueError, IndexError):
            print(Fore.RED + 'Selected server does not exists!' + Fore.RESET)
            raise ServerNotExist()

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
        if latest_sync_hash is None:
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
        self.set_latest_sync_hash(latest_commit.id)

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
        self.set_latest_sync_hash(latest_commit.id)

    def cherry_pick_commit(self, latest_sync_hash):
        """Cherry pick commits to sync"""
        print(Fore.YELLOW + "Choose commits to sync" + Fore.RESET)

        start = False
        if latest_sync_hash is None:
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
              "(" + str(commit.committer.offset) + ")" + Fore.RESET + " " + commit.message.replace('\n', ' ').replace('\r', '').strip() + Fore.MAGENTA + " - " + str(commit.committer.name) + Fore.RESET)

            sync_commit = input('Do you want to sync this commit? (Y): ')
            if sync_commit == "y" or sync_commit == "Y" or sync_commit == "":
                # process diff
                parent = self.find_parent_from_commit(commit)
                self.process_diff_files(parent, commit)

                # set latest hash
                self.set_latest_sync_hash(commit.id)
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
        host = self.ftpconfig.get_item(self.ftpname, 'host')
        remotedir = self.ftpconfig.get_item(self.ftpname, 'remotedir')
        localdir = self.ftpconfig.get_item(self.ftpname, 'localdir')
        username = self.ftpconfig.get_item(self.ftpname, 'username')
        password = self.ftpconfig.get_item(self.ftpname, 'password')

        self.ftpwrapper = FtpWrapper(host, remotedir, username, password)

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
            if localdir != '':
                process = delta.new_file.path.startswith(localdir, 0, len(localdir))
                remote_file_name = remote_file_name.replace(localdir, '', 1)
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

    def set_latest_sync_hash(self, commithash):
        """Update hash"""
        try:
            localdir = self.ftpconfig.get_item(self.ftpname, 'localdir')
            self.githash = GitHash(self.ftpname, localdir)
            self.githash.update(commithash)
        except Exception as error:
            print("error updating hash")
