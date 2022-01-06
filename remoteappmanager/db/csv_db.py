""" This module provides support for using CSV file as the database
of the remoteappmanager.

Expect the first row of the CSV file to contain headers shown as
follows.  The types of their values in the tables are shown in parantheses.

user.name (str)
    Name of the user.

application.image (str)
    Image name of the application.

policy.app_license (str)
    String containing application license (if required)

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
import uuid

from remoteappmanager.db.interfaces import (
    ABCDatabase, ABCApplication, ABCApplicationPolicy, ABCAccounting)
from remoteappmanager.db.exceptions import UnsupportedOperation
from remoteappmanager.utils import mergedocs, one


class CSVApplication(ABCApplication):
    pass


class CSVApplicationPolicy(ABCApplicationPolicy):
    pass


class CSVAccounting(ABCAccounting):
    pass


# FIXME: The user object could simply be a str (the username)
# We need this because HomeHandler._start_container takes an object with
# the username in its `name` attribute
class CSVUser(object):
    def __init__(self, id, name):
        self.name = name
        self.id = id


# Required headers of the CSV files
_HEADERS = ('user.name',
            'application.image',
            'policy.app_license',
            'policy.allow_home',
            'policy.allow_view',
            'policy.allow_common',
            'policy.volume_source',
            'policy.volume_target',
            'policy.volume_mode',
            'policy.allow_startup_data')


@mergedocs(ABCDatabase)
class CSVDatabase(ABCDatabase):
    """ Database class that reads a CSV file and is used by the
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
        self.users_by_id = {}
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
                user = self.users.get(user_name)

                if user is None:
                    id = len(self.users)
                    user = CSVUser(id=id, name=user_name)
                    self.users[user_name] = user
                    self.users_by_id[id] = user

                image = record[indices['application.image']]
                application = self.applications.setdefault(
                    image,
                    CSVApplication(
                        id=len(self.applications),
                        image=image
                    )
                )
                app_license = (
                    record[indices['policy.app_license']] or None)
                allow_home = record[indices['policy.allow_home']] == '1'
                allow_view = record[indices['policy.allow_view']] == '1'
                allow_common = record[indices['policy.allow_common']] == '1'
                volume_source = (record[indices['policy.volume_source']] or
                                 None)
                volume_target = (record[indices['policy.volume_target']] or
                                 None)
                volume_mode = (record[indices['policy.volume_mode']] or
                               None)
                allow_startup_data = record[
                                         indices['policy.allow_startup_data']
                                     ] == '1'

                application_policy = self.application_policies.setdefault(
                    (app_license,
                     allow_home,
                     allow_view,
                     allow_common,
                     volume_source,
                     volume_target,
                     volume_mode,
                     allow_startup_data),
                    CSVApplicationPolicy(
                        app_license=app_license,
                        allow_home=allow_home,
                        allow_view=allow_view,
                        allow_common=allow_common,
                        volume_source=volume_source,
                        volume_target=volume_target,
                        volume_mode=volume_mode,
                        allow_startup_data=allow_startup_data))

                # Save the configuration
                # Note that we don't filter existing duplicate entry
                self.all_records.setdefault(user.name, []).append(
                    CSVAccounting(
                        id=uuid.uuid4().hex,
                        user=user,
                        application=application,
                        application_policy=application_policy)
                )

    def get_user(self, *, user_name=None, id=None):
        if not one([user_name, id]):
            raise ValueError("Strictly one argument allowed")

        if user_name is not None:
            return self.users.get(user_name)
        elif id is not None:
            return self.users_by_id.get(id)
        else:
            raise RuntimeError("Impossible condition")  # pragma: no cover

    def get_accounting_for_user(self, user):
        if user is not None:
            return self.all_records.get(user.name, [])
        else:
            return []

    def create_user(self, user_name):
        raise UnsupportedOperation()

    def remove_user(self, *, user_name=None, id=None):
        raise UnsupportedOperation()

    def list_users(self):
        return list(self.users.values())

    def create_application(self, app_name):
        raise UnsupportedOperation()

    def remove_application(self, *, app_name=None, id=None):
        raise UnsupportedOperation()

    def list_applications(self):
        return list(self.applications.values())

    def grant_access(self, app_name, user_name, app_license,
                     allow_home, allow_view, volume, allow_startup_data):
        raise UnsupportedOperation()

    def revoke_access(self, app_name, user_name, app_license,
                      allow_home, allow_view, volume, allow_startup_data):
        raise UnsupportedOperation()

    def revoke_access_by_id(self, mapping_id):
        raise UnsupportedOperation()
