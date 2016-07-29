SimPhoNy Remote CHANGELOG
=========================

What's new in SimPhoNy Remote 0.6.0
-----------------------------------

Summary
~~~~~~~

- Added error payload to REST api (#186)
- Use dummy and virtual objects for testing (#172)
- Fix remoteappmanager config file consistency with docker-py (#171)
- Config file is made optional for remoteappmanager (#170)
- Add license in documentation (#169)
- Add REST Javascript client (#165)
- Add traitlets documenter for documentation (#163)
- Add troubleshoot page in documentation (#160)
- Bug fix: Timeout issue in tests (#167)
- Bug fix: Make sure remoteappdb closes the session on exit
- Bug fix: Source distribution with requirement files (#155)


What's new in SimPhoNy Remote 0.5.0
-----------------------------------

Summary
~~~~~~~

- Updated documentation (#147)
- Parameters for setting up docker client are now optional (#126)
- Formalise BadRequest error in the Rest API (#127)
- Add description to remoteappdb (#129)
- Supports parsing outputs from both docker `inspect_container` and
  `containers` (#133)
- Simplify the ReverseProxy (#114)
- Provide a set of dummy and virtual objects for better testing (#98)
- Bug fix: Subhandlers on the home page should raise instead of finish when
  error occurs (#123)
- Bug fix: Spawner's config_file_path should be configurable from jupyterhub
  config (#124)
- Bug fix: Deprecation warning from Traitlets (#135)
- Bug fix: Empty file created if target sqlite database does not exist (#139, 122)
- Bug fix: SSL failure for auto ssl version (#144)


What's new in SimPhoNy Remote 0.4.0
-----------------------------------

Summary
~~~~~~~

- Experimental REST API and CLI program to control containers from the
  command line (#7)
- Support for arbitrary database implementations (#66)
- Added remoteappdb `--verify` option to check against the docker repo for
  matching images (#58)
- Enabled Foreign Key and on cascade delete for sqlite database (#56)
- Introduced makefile for basic deployment tasks (#68)
- User.orm_user is now User.account (#67)
- Asynchronous user verification with the jupyter hub is now in place (#37)
- Consistently differentiate between url and urlpath in parameters, where
  possible (#54)
- Container.host_url now checks for None port (#63)
- Isolated sqlalchemy sessions for the base handler (#71)
- verify_token now returns a dictionary with user details. (#77)
- Bug: ui_names no longer appearing (#64)
- Bug: test error for sqlalchemy usage with multiple threads. (#99)
- Bug: fixed test error message relative to unclosed files. (#60)


What's new in SimPhoNy Remote 0.3.0
-----------------------------------

Summary
~~~~~~~

- Introduced a more generic configuration of available users and images
  through a CSV file (#33, #41)
- Internally refactored configuration handling (#40)
- Simplified database layout by removing Teams (#32)
- Added functionality to remove users and applications from database via
  remoteappdb CLI application (#28)
- Attaching of workspace (#4)
- Added API autodoc documentation (#57)
- Improved testing and coverage (#5)
- Improved error message when unable to create temporary directory (#53)
- Fixed regression with View button not working anymore (#43)

What's new in SimPhoNy Remote 0.2.0
-----------------------------------

Summary
~~~~~~~

- Introduced access control for images and users by means of a database.
  Additionally, a CLI utility to modify the content of the database has
  been provided (#8)
- Added readthedocs documentation (#12)
- Container URL now contains a base32 encoded unique identifier, 
  instead of the docker container id. (#18)
- Introduced authentication of the user for the application (#24)
- Improved handling of failures in starting containers (#6, #14, #15)

What's new in SimPhoNy Remote 0.1.0
-----------------------------------

Summary
~~~~~~~

Initial release. 

- A jupyterhub application handling multiple docker containers per user (PAM authentication)
- A specialized spawner to handle the correct initialization of the user app
- Support attaching home volumes to containers
- Support attaching common volumes to containers
