"""FTP config"""
from configparser import ConfigParser, NoOptionError, NoSectionError


class ServerNotExist(Exception):
    pass

class FtpConfig:
    """FTP config class"""
    config_filename = ".gitftp"

    def __init__(self):
        """Initialize"""
        self.parser = ConfigParser()
        try:
            with open(self.config_filename) as f:
                self.parser.read_file(f)
        except FileNotFoundError:
            self.__write()

    def set(self, section, host, username, password, remotedir, localdir):
        """Set new server configuration"""
        if not self.has_section(section):
            self.parser.add_section(section)

        self.parser.set(section, 'type', 'ftp')
        self.parser.set(section, 'host', host)
        self.parser.set(section, 'username', username)
        self.parser.set(section, 'password', password)
        self.parser.set(section, 'remotedir', remotedir)
        self.parser.set(section, 'localdir', localdir)

        self.__write()

    def set_item(self, section, item, value):
        """Set single item for server configuration"""
        if self.has_section(section):
            self.parser.set(section, item, value)

        self.__write()

    def get_item(self, section, item):
        """Get item for server configuration"""
        try:
            return self.parser.get(section, item)
        except NoOptionError:
            return None
        except NoSectionError:
            return None

    def remove_item(self, section, item):
        """Remove item for server configuration"""
        self.parser.remove_option(section, item)
        self.__write()

    def get_section(self, section):
        """Get server configuration"""
        if self.has_section(section):
            return self.parser.items(section)
        else:
            return None

    def list_sections(self):
        """List all server configurations"""
        return self.parser.sections()

    def remove_section(self, section):
        """Remove server configuration"""
        removed = self.parser.remove_section(section)
        if removed:
            self.__write()

        return removed

    def has_section(self, section):
        """Check if configuration exist"""
        return self.parser.has_section(section)

    def __write(self):
        """Write configuration file"""
        with open(self.config_filename, 'w+') as configfile:
            self.parser.write(configfile)
