""" This module provides support for using CSV file as the database
of the remoteappmanager.

Expect the first row of the CSV file to contain headers shown as
follows.  The types of their values in the tables are shown in parantheses.

user.name (str)
    Name of the user.

application.image (str)
    Image name of the application.

policy.allow_home (str)
    Is home directory mounted (1 - true, 0 - false).

policy.allow_view (int)
    Is the application viewable by others (1 - true, 0 - false).

policy.allow_common (int)
    Is the common data volume available (1 - true, 0 - false).
    If true, requires definitions of volume_source, volume_target
    and volume_mode.

policy.volume_source (str)
    Path for the common data volume on the host machine.
    If undefined, common data volume is not available.

policy.volume_target (str)
    Target mount point of the common data volue in the application.
    If undefined, common data volume is not available.

policy.volume_mode (str)
   Mode for read/write access ('ro' - read-only, 'rw' - read-write).
   If undefined, common data volume is not available

Note
----

- Additional columns are ignored.
- This reader does not try to eliminate duplicated application and policy
  record for a given user.  It faithfully reads the CSV file and returns
  what it says.

"""

import csv
import hashlib

from remoteappmanager.db.interfaces import (
    ABCAccounting, ABCApplication, ABCApplicationPolicy)
from remoteappmanager.db.exceptions import UnsupportedOperation
from remoteappmanager.utils import mergedocs


class CSVApplication(ABCApplication):
    pass


class CSVApplicationPolicy(ABCApplicationPolicy):
    pass


# FIXME: The user object could simply be a str (the username)
# We need this because HomeHandler._start_container takes an object with
# the username in its `name` attribute
class CSVUser(object):

    def __init__(self, name):
        self.name = name


# Required headers of the CSV files
_HEADERS = ('user.name',
            'application.image',
            'policy.allow_home',
            'policy.allow_view',
            'policy.allow_common',
            'policy.volume_source',
            'policy.volume_target',
            'policy.volume_mode')


@mergedocs(ABCAccounting)
class CSVAccounting(ABCAccounting):
    """ Accounting class that reads a CSV file and is used by the
    remoteappmanager.  Currently only accepts one csv file.
    """

    def __init__(self, csv_file_path, **kwargs):
        """ Initialiser

        Parameters
        ----------
        csv_file_path : str
            File path for the CSV file

        **kwargs
            optional keyword arguments for open(csv_file_path)
        """
        self.csv_file_path = csv_file_path

        # Let's keep everything in memory for now
        self.all_records = {}
        self.users = {}
        self.applications = {}
        self.application_policies = {}

        with open(self.csv_file_path, **kwargs) as csv_file:
            reader = csv.reader(csv_file)

            # Validate the headers
            headers = next(reader)
            missing_headers = set(_HEADERS) - set(headers)
            if missing_headers:
                msg = ("Expect the first row to contain headers. "
                       "Missing headers: {}")
                raise ValueError(msg.format(", ".join(missing_headers)))

            # Map indices for the columns
            indices = dict(zip(_HEADERS,
                               (headers.index(header) for header in _HEADERS)))

            for count, record in enumerate(reader):
                user_name = record[indices['user.name']]
                user = self.users.setdefault(user_name,
                                             CSVUser(name=user_name))

                image = record[indices['application.image']]
                application = self.applications.setdefault(
                    image,
                    CSVApplication(image=image))

                allow_home = record[indices['policy.allow_home']] == '1'
                allow_view = record[indices['policy.allow_view']] == '1'
                allow_common = record[indices['policy.allow_common']] == '1'
                volume_source = (record[indices['policy.volume_source']] or
                                 None)
                volume_target = (record[indices['policy.volume_target']] or
                                 None)
                volume_mode = (record[indices['policy.volume_mode']] or
                               None)

                application_policy = self.application_policies.setdefault(
                    (allow_home,
                     allow_view,
                     allow_common,
                     volume_source,
                     volume_target,
                     volume_mode),
                    CSVApplicationPolicy(
                        allow_home=allow_home,
                        allow_view=allow_view,
                        allow_common=allow_common,
                        volume_source=volume_source,
                        volume_target=volume_target,
                        volume_mode=volume_mode))

                # Save the configuration
                # Note that we don't filter existing duplicate entry
                mapping_id_prehex = '_'.join((application.image, str(count)))
                self.all_records.setdefault(user.name, []).append(
                    (hashlib.md5(mapping_id_prehex.encode('u8')).hexdigest(),
                     application,
                     application_policy))

    def get_user_by_name(self, user_name):
        return self.users.get(user_name)

    def get_apps_for_user(self, user):
        if user:
            return tuple(self.all_records.get(user.name, ()))
        else:
            return ()

    def create_user(self, user_name):
        raise UnsupportedOperation()

    def remove_user(self, user_name):
        raise UnsupportedOperation()

    def list_users(self):
        return list(self.users.values())

    def create_application(self, app_name):
        raise UnsupportedOperation()

    def remove_application(self, app_name):
        raise UnsupportedOperation()

    def list_applications(self):
        return list(self.applications.values())

    def grant_access(self, app_name, user_name,
                     allow_home, allow_view, volume):
        raise UnsupportedOperation()

    def revoke_access(self, app_name, user_name,
                      allow_home, allow_view, volume):
        raise UnsupportedOperation()
