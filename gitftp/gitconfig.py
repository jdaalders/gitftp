"""GIT config"""


class GitConfig(object):
    """GIT Config class"""

    def __init__(self, repo):
        """Initialize"""
        self.repo = repo

    def get(self, name, regex=None):
        """Get config"""

        try:
            result = self.repo.config.get_multivar(name, regex).next()
        except StopIteration:
            result = None

        return result

    def set(self, name, value):
        """Set root directory on the server"""
        regex = self.get(name)
        if regex is None:
            regex = "/"

        self.repo.config.set_multivar(name, regex, value)
