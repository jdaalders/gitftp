"""FTP Config"""
import unittest
import os
from gitftp import FtpConfig

class FtpConfigTestCase(unittest.TestCase):
    """FTP Config Test Class"""

    def setUp(self):
        """SetUp test case"""
        self.config = FtpConfig()

    def tearDown(self):
        """TearDown test case"""
        os.remove('.gitftp')

    def __create_section(self, section):
        host = "ftp://example.com"
        username = "john"
        password = "doe"
        remotedir = "httpdocs"
        localdir = "src"

        self.config.set(section, host, username, password, remotedir, localdir)
        self.assertTrue(self.config.has_section(section))

    def test_add(self):
        """Test adding a new server configuration"""
        section = "production"
        host = "ftp://example.com"
        username = "john"
        password = "doe"
        remotedir = "httpdocs"
        localdir = "src"

        self.config.set(section, host, username, password, remotedir, localdir)
        self.assertTrue(self.config.has_section(section))

    def test_remove_section(self):
        """Test remove server configuration"""
        section = 'test'
        self.__create_section(section)

        removed = self.config.remove_section(section)
        self.assertTrue(removed)
        self.assertFalse(self.config.has_section(section))

    def test_change_section(self):
        """Test changing server configuration"""
        section = 'test'
        self.__create_section(section)

        host = "ftp://example.com"
        username = "john"
        password = "doe"
        remotedir = "htdocs"
        localdir = "none"

        self.config.set(section, host, username, password, remotedir, localdir)
        self.assertTrue(self.config.has_section(section))

        # get section
        result = self.config.get_section(section)
        expected = [('host', host), ('username', username), ('password', password),\
          ('remotedir', remotedir), ('localdir', localdir)]
        self.assertEqual(result, expected)

    def test_set_existing_item(self):
        """Test changing item from server configuration"""
        section = 'test'
        self.__create_section(section)

        item = 'host'
        value = 'http://example.com'
        self.config.set_item(section, item, value)

        expected = value
        result = self.config.get_item(section, item)
        self.assertEqual(result, expected)

    def test_get_item(self):
        """Test get item from server configuration"""
        section = 'test'
        self.__create_section(section)

        # get host
        result = self.config.get_item(section, 'host')
        self.assertEqual(result, 'ftp://example.com')

    def test_get_item_from_non_existing_section(self):
        """Test get item from non existing server configuration"""
        section = 'test'
        self.__create_section(section)

        # get host
        result = self.config.get_item('non_existing', 'host')
        self.assertEqual(result, None)

    def test_remove_item(self):
        """Test get server configuration"""
        section = 'test'
        self.__create_section(section)

        #remove item
        self.config.remove_item(section, 'host')

        # get host
        result = self.config.get_item(section, 'host')
        self.assertEqual(result, None)

    def test_get_section(self):
        """Test get server configuration"""
        section = 'test'
        self.__create_section(section)

        # get section
        result = self.config.get_section(section)
        expected = [('host', 'ftp://example.com'), ('username', 'john'), ('password', 'doe'),\
          ('remotedir', 'httpdocs'), ('localdir', 'src')]
        self.assertEqual(result, expected)

    def test_get_non_existing_section(self):
        """Test non existing server configuration"""
        section = "non_existing"
        result = self.config.get_section(section)
        self.assertEqual(result, None)

    def test_list(self):
        """Test list all server configurations"""
        # add new section
        section = 'test1'
        self.__create_section(section)

        # add new section
        section = "test2"
        self.__create_section(section)

        # get list
        result = self.config.list_sections()

        #verify list
        expected = ['test1', 'test2']
        self.assertListEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
