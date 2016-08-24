Selenium Test
-------------

This directory contains tests on the live website using selenium.
To create a new selenium test:

- Install selenium and the Selenium IDE as specified at http://www.seleniumhq.org
- Start Selenium IDE from the Firefox Tools menu.
- Selenium works by recording your operations with the browser
  and creating a script to reproduce the same operations 
  programmatically. Create various testcases for all the possible 
  use cases of the site
- Once happy with the test, export the test as a python script using
  File -> Export TestCase as... -> Python 2 - unittest - webdriver
- The generated python script will need some adjustments. 
  Modify it by hand appropriately (for example, using the base class
  SeleniumTestBase for common functionality)


At the moment, tests in the native format are not saved. Please consider
this option if the testsuite grows larger.
