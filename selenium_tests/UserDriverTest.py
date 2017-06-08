# -*- coding: utf-8 -*-
import contextlib
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class UserDriverTest(RemoteAppDriverTest):
    def setUp(self):
        RemoteAppDriverTest.setUp(self)
        self.login("test")

    def select_application(self, index=0):
        self.click_first_element_located(By.ID, "application-entry-{}".format(index))

    def open_application_settings(self):
        self.click_first_element_located(By.ID, "application-settings")

    def stop_application(self):
        self.click_first_element_located(By.ID, "stop-button")

    def start_application(self):
        self.click_first_element_located(By.ID, "start-button")

    def wait_until_application_running(self):
        self.wait_until_presence_of_element_located(By.ID, "application")

    def wait_until_application_stopped(self):
        self.wait_until_text_inside_element_located(By.ID, "start-button", "Start")

    def wait_until_application_list_loaded(self):
        self.wait_until_invisibility_of_element_located(By.ID, "loading-spinner")

    @contextlib.contextmanager
    def running_container(self, index=0):
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
