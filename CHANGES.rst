SimPhoNy Remote CHANGELOG
=========================

What's new in SimPhoNy Remote 2.1.0
-----------------------------------


What's new in SimPhoNy Remote 2.0.0
-----------------------------------

- Switch to Vue for both admin interface and user interface (#400, #402, #405, 
  #407, #410, #411, #412, #413, #414, #420, #422, #423, #428, #431, #433, #434, 
  #436, #437, #438, #440, #442, #443, #446, #447, #448, #450, #451, #456, #459,
  #465, #467, #468, #471, #472, #473, #480, #481, #482, #489, )
- Added search. Now only applications matching will be shown (#417, #427)
- Added share button to extract the URL of the container (#469)
- First application is now automatically selected (#418)
- Adapted backend for new Vue based interface:
    - Usage of new tornado-webapi interface (#403)
    - Added REST resource for statistics, needed by #395 (#406)
    - Server side admin support for new Admin interface (#425)
- Renamed some entities to more appropriate names (#419)
  - The term Accounting now refers exclusively to the relationship table
    connecting users, applications and policies.
  - The config file accounting_class and accounting_kwargs are now
    database_class and database_kwargs.
  - AppAccounting is now ORMDatabase. Similarly, CSVAccounting is now
    CSVDatabase.
  - The above two break compatibility with the old configuration files.
    Old configuration files must be changed both in the options
    and the class they refer to.
  - Added alembic file to support the migration (#445)
- Removed CDN usage for full intranetwork compatibility.
- Upgraded configurable-http-proxy to 2.0.1 (#394)
- Added statistics in the main (Home) Admin panel. (#395)
- Pinned against pre-release version of Jupyterhub due to deprecation and
  incompatibility with authenticators (#396)
- Extracted application name in the topbar (#462)

- Fixes:
    - Compatibility with some adblockers for google analytics (#379) 
    - Added random token to container name to prevent conflict during stop 
      of containers (#381)
    - Documented behavior with uppercase-lowercase names with github 
      authentication. (#386)
    - Performs re-registration of container when the jupyterhub service is 
      stopped, to regain access to containers (#387)
    - Example jupyterhub configuration file allows now to work with no external
      interfaces (#409)
    - Using node 6 for the builds and prevent the use of node 4 from travis to 
      workaround disrupting ECONNRESET issues (#488)
    - Upgraded astor to master to fix python 3.5 incompatibility during 
      documentation build (#494)
    - Skip containers that are not found while checking container.items (#478)

- Refactor:
    - Virtual docker has been cleaned up completely (#389)
    - Container manager deprecated find methods have been removed in favor
      of a different interface. (#391)
    - Use webpack to include javascript code (#452, #458)
    - Use of ES6 for the main development (#457)
    - Changed frontend file layout (#454, #460)
    - Removed underscore and moment from the javascript dependencies (#455)
    - Replaced jshint with eslint (#463)

- Other:
    - Made tests less verbose with logging (#408)
    - Reduced verbosity at build (#424)

What's new in SimPhoNy Remote 1.1.0
-----------------------------------

- Use container provenance information to prevent access to unrelated 
  containers or simphony-remote instances (#361)
- Upgraded tornado WebAPI to 0.5.0 (#335, #365, #340)
- Interface overhaul. Introduced Admin-LTE frontend (#346)
- Upgraded against jupyterhub 0.8.0.dev0 (#355, #358)
- Introduced "realms" to hold container provenance in case of shared docker 
  server (#361)
- Added dynamic whitelist for GitHub login (#351, #359, #364)
- Fixes: 
    - forever stuck spinner in case of docker internal failure (#336)
    - Documented unexpected behavior reported in #305: containers not visible 
      if the per-user server is already running (#342)
    - Incorrect username in admin panel has been fixed (#353)
    - Removed selenium_test from deployment (#356)
    - Establish correct keyboard focus when canvas is made visible (#362)
- Refactor: 
    - Extracted macro in jinja template to a separate file (#337)
    - Cleaned up javascript utils module into separate files (#339)
    - Use of table macro to reduce template duplication (#341)
    - Use setup.py to generate the version.py file (#357)
    - Made async docker client instance in ContainerManager private (#360)
- Other:
    - Fixed changes in ubuntu dependency builds (#352)
    - Added some basic example configuration files (#363)

What's new in SimPhoNy Remote 0.9.0/1.0.0
-----------------------------------------

Summary
~~~~~~~

- Administrative Web interface (#284)
- Introduced runtime label namespace to differentiate labels added by the docker
  build process from those added at startup (#292)
- The associated absolute URL path is now attached to the running container in a
  runtime label (#311)
- Remoteappdb now accepts the database path as a mandatory argument, instead of
  an option entry (#291)
- Accounting interface change: User can now be obtained by user name or id. (#308)
- Accounting interface change: Extended accounting to perform administrative actions (#304)
- Docker container object now provides the user that started the container (#302)
- Web API resources are now under webapi, instead of restresources (#317)
- Upgraded dependency to tornado WebAPI 0.4.0 (#328)
- Cleanup of WebAPI testing (#324) JavaScript (#320), stale code (#319)
- Moved JupyterHub support classes to specific subpackage (#298)
- Introduced authenticated decorator for resources that does not 
  perform redirection like web.authenticated (#294)
- Pinned requirements to specific versions (#289)
- UI:
  - Added fading in effect when applications are shown
- Refactoring:
  - Extracted volume string parsing routine (#303)
  - Extracted base application object (#301)
  - Extracted base spawner (#300)
  - remoteappmanager entry point is now part of the CLI package (#299)
  - Removed test setting of PROXY_API_TOKEN (#288)
- Security Fix:
    - Prevent another user to stop another user's container through its
      url_id (#310)

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
