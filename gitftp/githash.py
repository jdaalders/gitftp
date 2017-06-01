"""Git Hash"""
from configparser import ConfigParser, NoOptionError, NoSectionError
from .ftpwrapper import FtpWrapper
from .ftpconfig import FtpConfig, ServerNotExist
from common.configwriter import ConfigWriter

class GitHash(ConfigWriter):
    """Git hash class"""
    filename = ".githash"

    def __init__(self, section, localdir):
        """Initialize"""
        self.section = section
        self.localdir = localdir
        self.full_filename = str(self.localdir) + '/' + str(self.filename)
        ConfigWriter.__init__(self, self.full_filename)
		
        self.ftpconfig = FtpConfig()

        if not super().has_section(self.section):
            super().add_section(self.section)

    def get(self):
        """Get hash"""
        try:
            host = self.ftpconfig.get_item(self.section, 'host')
            remotedir = self.ftpconfig.get_item(self.section, 'remotedir')
            username = self.ftpconfig.get_item(self.section, 'username')
            password = self.ftpconfig.get_item(self.section, 'password')

            ftpwrapper = FtpWrapper(host, remotedir, username, password)
            ftpwrapper.download(self.filename, self.localdir, False)
			
            return super().get(self.section, 'hash')
			
        except NoOptionError:
            return None
        except NoSectionError:
            return None
        except Exception:
            return None
			
    def update(self, hash):
        """Update hash"""
        try:
            host = self.ftpconfig.get_item(self.section, 'host')
            remotedir = self.ftpconfig.get_item(self.section, 'remotedir')
            username = self.ftpconfig.get_item(self.section, 'username')
            password = self.ftpconfig.get_item(self.section, 'password')

            ftpwrapper = FtpWrapper(host, remotedir, username, password)
            ftpwrapper.download(self.filename, self.localdir, False)
			
            super().set(self.section, 'hash', hash)
            ftpwrapper.upload(self.full_filename, self.filename)
			
        except NoOptionError:
            return None
        except NoSectionError:
            return None
        except Exception:
            return None
