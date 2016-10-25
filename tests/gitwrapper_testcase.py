"""Git Wrapper"""
import unittest
import os
from gitftp import GitWrapper
from gitftp import FtpConfig

class GitWrapperTestCase(unittest.TestCase):
    """GIT Wrapper Test Class"""
    section = "test"

    def setUp(self):
        """SetUp test case"""
        self.config = FtpConfig()

        # setup server configuration
        host = "ftp://example.com"
        username = "john"
        password = "doe"
        remotedir = "httpdocs"
        localdir = "src"

        self.config.set(self.section, host, username, password, remotedir, localdir)
        self.assertTrue(self.config.has_section(self.section))

        self.gitwrapper = GitWrapper(None, self.section)

    def tearDown(self):
        """TearDown test case"""
        # os.remove('.gitftp')
        pass

    def test_set_latest_sync_hash(self):
        """Test adding a new server configuration"""
        value = 'abc'
        self.gitwrapper.set_latest_sync_hash(value)

        # verify result
        ftpconfig = FtpConfig()
        result = ftpconfig.get_item(self.section, 'latest')

        self.assertEqual(result, value)

if __name__ == '__main__':
    unittest.main()
