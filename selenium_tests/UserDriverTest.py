# -*- coding: utf-8 -*-
import contextlib
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class UserDriverTest(RemoteAppDriverTest):
    def setUp(self):
        RemoteAppDriverTest.setUp(self)
        self.login("test")

    def select_application(self, index=0):
        """ Select an application in the application list by clicking on it.
        Parameters
        ----------
        index: Integer
            The index of the application you want to select

        Example
        -------
        select_application(1)
        select_application(0)
        """
        self.click_first_element_located(By.ID, "application-entry-{}".format(index))

    def open_application_settings(self):
        """ Open the application settings dropdown.
        """
        self.click_first_element_located(By.ID, "application-settings")

    def stop_application(self):
        """ Click on the stop button. It assumes that the application settings
        menu is opened and that the application is running. This will stop the
        currently selected application.
        """
        self.click_first_element_located(By.ID, "stop-button")

    def start_application(self):
        """ Click on the start button. It assumes that the currently selected
        application is stopped.
        """
        self.click_first_element_located(By.ID, "start-button")

    def wait_until_application_running(self):
        """ Wait until the currently selected application is running.
        """
        self.wait_until_presence_of_element_located(By.ID, "application")

    def wait_until_application_stopped(self):
        """ Wait until the currently selected application is stopped.
        """
        self.wait_until_text_inside_element_located(By.ID, "start-button", "Start")

    def wait_until_application_list_loaded(self):
        """ Wait until the application list is completely loaded and displayed
        """
        self.wait_until_invisibility_of_element_located(By.ID, "loading-spinner")

    @contextlib.contextmanager
    def running_container(self, index=0):
        """ Context manager with a running application at the given index. The
        application is stopped at the end.
        """
        self.wait_until_application_list_loaded()

        self.select_application(index)
        self.start_application()

        try:
            yield
        finally:
            self.select_application(index)
            self.wait_until_application_running()
            self.open_application_settings()
            self.stop_application()
            self.wait_until_application_stopped()

    def tearDown(self):
        self.logout()
        RemoteAppDriverTest.tearDown(self)
