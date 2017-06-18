# GitFTP
GitFTP let you manage deploying your commits to multiple FTP servers.


## Commands

### Add FTP server
Add a FTP server configuration. Specify a name for the server and an url.
The following fields can be filled in to configure the FTP server:
- __username__ (FTP server username)
- __password__ (FTP server password)
- __local directory__ (The local directory which needs to be synchronized. For instance if you use a 'src' directory you can specify this to only sync the particular directory)
- __remote directory__ (The remote directory where you want to upload your changes)
```bash
# Add FTP server configuration
$ git ftp add production ftp://example.com
FTP: add server settings

# Fill in the ftp username
username:

# Fill in the ftp password
password:

# Fill in the ftp password
local directory:

# Fill in the ftp password
remote directory:

FTP server 'production' added.
```

### Remove FTP server
Remove a FTP configuration. Use the remove command with or without specifying a server configuration
```bash
# Remove FTP server configuration
$ git ftp remove production

# or
$ git ftp remove
```

### List all servers
The 'servers' command will list all available FTP server configurations.
```bash
# List all server
$ git ftp servers
```

### Deploy
Deploy changes from git to a FTP server. Use the deploy command with or without specifying a server configuration.
If called without specifying a server configuration you will be asked which configuration you would like to use.
```bash
# Deploy changes to FTP server
$ git ftp deploy production

# or
$ git ftp deploy
```

The FTP configuration will keep track of your sync history. Only the latest changes will be transferred to the FTP server.
If your one commit behind with syncing to the server it will be automatically synced when calling the deploy command.

If your behind more then one commits the deploy command will give you a few options:

1. __catchup__ (catchup with the latest commit, so sync every commit)
2. __sync only latest__ (sync only the latest commit and skip everything in between)
3. __choose commits to sync__ (cherry pick which commit you want to sync to the FTP server)


## Development
### Dependencies
- [pygit2](http://www.pygit2.org/)
- [ConfigParser](https://docs.python.org/2/library/configparser.html#module-ConfigParser)
- [Colorama](https://pypi.python.org/pypi/colorama)

### Build
Build a distribution version can be done by installing 'pyinstaller'. pip install pyinstaller
After installing pyinstaller run:
```bash
pyinstaller --onefile git-ftp.py
```

Copy the executable to the git directory.
On a Mac it's:
```bash
sudo cp dist/git-ftp /usr/local/git/bin/git-ftp
```
