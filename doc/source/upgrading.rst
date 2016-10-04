Upgrading from a pre-existing version
-------------------------------------

Upgrade 0.8.0 to 0.9.0
~~~~~~~~~~~~~~~~~~~~~~

If you are using sqlite to manage your users, the sqlite database has changed
and need to be upgraded. 
We use alembic to manage the migration.  Make sure you have alembic installed
in your virtual environment::
    
    pip install alembic

Then edit the ``alembic.ini`` file to make sure the ``sqlalchemy.url`` 
entry is pointing at the correct database.

After this step is performed, issue the following command::

    alembic upgrade head

This will upgrade your database.
