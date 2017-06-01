"""Config Writer"""
from configparser import ConfigParser, NoOptionError, NoSectionError


class ConfigWriter:
    """Config Writer class"""

    def __init__(self, config_filename):
        """Initialize"""
        self.parser = ConfigParser()
        self.config_filename = config_filename
		
        try:
            with open(self.config_filename) as f:
                self.parser.read_file(f)
        except FileNotFoundError:
            self.__write()
			
    def set(self, section, item, value):
        """Set single item for section"""
        self.parser.set(str(section), str(item), str(value))

        self.__write()

    def get(self, section, item):
        """Get item for section"""
        try:
            return self.parser.get(section, item)
        except NoOptionError:
            return None
        except NoSectionError:
            return None

    def remove(self, section, item):
        """Remove item for section"""
        self.parser.remove_option(section, item)
        self.__write()

    def get_section(self, section):
        """Get section configuration"""
        if self.has_section(section):
            return self.parser.items(section)
        else:
            return None

    def add_section(self, section):
        """Set new server configuration"""
        if not self.has_section(section):
            self.parser.add_section(section)
        self.__write()

    def list_sections(self):
        """List all sections"""
        return self.parser.sections()

    def remove_section(self, section):
        """Remove section"""
        removed = self.parser.remove_section(section)
        if removed:
            self.__write()

        return removed

    def has_section(self, section):
        """Check if section exist"""
        return self.parser.has_section(section)

    def __write(self):
        """Write configuration file"""
        with open(self.config_filename, 'w+') as configfile:
            self.parser.write(configfile)
