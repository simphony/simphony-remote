import os
from oauthenticator import GitHubOAuthenticator
from traitlets.config import LoggingConfigurable
from traitlets import Unicode, Float, Set


class FileWhitelistMixin(LoggingConfigurable):
    """
    """

    #: The path of the whitelist file.
    whitelist_file = Unicode()

    #: When the file was last modified, so that we can reload appropriately.
    _whitelist_file_last_modified = Float()

    #: Cached whitelist to return every time the file hasn't changed.
    _whitelist = Set()

    @property
    def whitelist(self):
        try:
            cur_mtime = os.path.getmtime(self.whitelist_file)
            print(os.path.getsize(self.whitelist_file))
        except FileNotFoundError:
            # empty set means everybody is allowed
            return {}
        except Exception:
            # For other exceptions, assume the file is broken, log it
            # and return what we have.
            self.log.exception("Unable to access whitelist.")
            return self._whitelist

        if cur_mtime <= self._whitelist_file_last_modified:
            # File older than last change.
            # keep using the current cached whitelist
            return self._whitelist

        self.log.info("Whitelist file more recent than the old one. "
                      "Updating whitelist.")

        # File has changed, parse its new content and reapply
        try:
            with open(self.whitelist_file, "r") as f:
                whitelisted_users = set(x.strip() for x in f.readlines())
        except FileNotFoundError:
            return {}
        except Exception:
            self.log.exception("Unable to access whitelist.")
            # For other exceptions, assume the file is broken
            return self._whitelist

        self._whitelist = whitelisted_users
        self._whitelist_file_last_modified = cur_mtime

        return self._whitelist


class GitHubWhitelistAuthenticator(FileWhitelistMixin, GitHubOAuthenticator):
    """A github authenticator that also verifies that the
    user belongs to a specified whitelisted user as provided
    by an external file (so that we don't have to restart
    the service to change the whitelisted users"""
