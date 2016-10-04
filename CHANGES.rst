SimPhoNy Remote CHANGELOG
=========================

What's new in SimPhoNy Remote 0.9.0
-----------------------------------

Summary
~~~~~~~

- Remoteappdb now accepts the database path as a mandatory argument
- Provided upgrading functionality for remoteappmanager.db sqlite database via alembic. (#295)
- Support for admin user both for the CSV Accounting and the sqlite database. (#296)


What's new in SimPhoNy Remote 0.8.0
-----------------------------------

Summary
~~~~~~~

- Introduced Google Analytics support for start of Applications (#274).
- Support for passing configurable data at application startup (#255, #257, #260, #263, #264, #266)
  Documentation of the resulting docker image protocol (#278)
- Virtual user workspace is now created once and preserved, with a identifiable name (#270)
- Launching or viewing application now opens a new window (#269)
- Makefile rule and documentation for docker upgrade on Ubuntu 14.04 host (#249)
- Introduced npm/bower package management. Removed now irrelevant files. (#272, #273, #275)
- UI:
    - Added spinner during loading of applications. Added message in case of no applications available (#252)
    - beautification (#265)
- CI: 
    - Removed Paraview image retrieval (#256)
    - Better Travis output using before_script to perform devdeps installation. (#267)
    - Added test coverage for JavaScript code with Blanket (#276)
- Refactor: 
    - Major overhaul of JavaScript layer (#250)
    - Finalized porting of WebAPI to tornadowebapi (#254)
- Fix:
    - Reporting error in case of double start/stop request, removing a potential race condition (#279)
    - Documented command line start request behavior for already started container (#280)


What's new in SimPhoNy Remote 0.7.0
-----------------------------------

Summary
~~~~~~~

- Addressed issues for general support for Docker containers holding Web applications 
  (jupyter notebook, filemanager) available as simphony-remote-docker 0.3.0.
- REST+ajax based retrieval of available applications (#209, #214)
- Show application policy information in application list (#242)
- Preparation for REST framework extraction: 
    - factored out authenticator code from the BaseHandler (#215)
    - soft deprecation of subpackage (#236)
- Upgraded dependencies to jupyterhub 0.7.0.dev0 (#217), configurable-http-proxy (#219)
  to fix forwarding bugs in jupyterhub. 
- Pinned request package dependency to 2.10.0 due to dockerpy constraints (#222)
- Renamed Spawner to SystemUserSpawner (#205)
- Added linting and testing infrastructure for javascript (#200)
- Documentation fixes and refactorings:
    - General fixes (#179, #198, #199, #202, #232, #233) 
    - Use of autosummary for API extraction (#194, #234) 
    - Extracted traitlets documenter in a separate repository (#210)
- Migrated tests under the appropriate paths in the package tree (#196)
- Command remoteapprest prints out only essential (UI name) application information, 
  instead of the whole content of the request. (#230)
- Removed the need for sudo in configurable-http-proxy installation (#244). Installation is now local.
- Support for Ubuntu 16.04 (#243)
    - Pinned dockerpy package dependency to 1.8.1
    - Update deployment docs for Ubuntu 16.04
- Fix: Failing selenium tests due to unexpected client-side selenium behavior (#203)
- Fix: Added missing jupyterhub_config.py from MANIFEST.in (#206), fixed other paths (#207)
- Fix: Exclude applications in the REST item list when not available (#225)
- Fix: Handle failure of ajax retrieval so that partial failure is tolerated (#223)
- Refactor: removed start/stop_spawner (#208)
- Refactor: cleaned up docker label namespacing (#212)


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
