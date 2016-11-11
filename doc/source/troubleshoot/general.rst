A new user does not see the applications I am adding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You have to restart the user server. As a jupyterhub administrator, go to

https://your.jupyterhub.url/hub/admin

and restart the user server.

This problem will appear under this circumstance:
1. User who is not in the remoteappmanager db yet performs a login. 
2. Admin adds User to remoteappmanager db, and grants him some applications.
3. User will not see the applications.

The reason is the following: when the user first performs the login, the
remoteappmanager subprocess is started. The authentication mechanism looks the
user up in the remoteappmanager database, does not find it, and therefore sets
account to None.  This operation is never performed again, so the user remains
None even if later on it is added to the database. Only by restarting 
remoteappmanager the lookup is performed again.

It is debatable if this behavior is a bug or not (after all, bash also won't
alter your current enviroment if root changes /etc/bashrc, and you will have to
logout to get the new environment). Issue #305 debates this point.
