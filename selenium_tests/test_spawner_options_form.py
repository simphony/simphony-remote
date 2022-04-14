# -*- coding: utf-8 -*-
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class TestSpawnerOptionsForm(RemoteAppDriverTest):

    def admin_logout(self):
        """ Admin Logout. Ensures user session is stopped before performing logout.
        This action should be generally used whenever the Spawner options form is
        presented during logins so that it is correctly displayed for the next test
        runner.
        """
        self.driver.get(self.base_url + "/home")

        self.click_first_element_located(By.ID, "stop")
        self.click_first_element_located(By.ID, "logout")
        self.wait_until_text_inside_element_located(By.CSS_SELECTOR, "div.auth-form-header", "Sign in")

    def test_admin_login_default_session(self):
        self.login("admin")

        self.click_first_element_located(By.ID, "start")
        self.click_first_element_located(By.CSS_SELECTOR, "input.btn")
        self.click_first_element_located(By.ID, "start")

        self.wait_until_text_inside_element_located(
            By.CSS_SELECTOR, ".header", "ADMIN")

    def test_admin_login_user_session(self):
        self.login("admin")

        self.click_first_element_located(By.ID, "start")
        self.click_first_element_located(
            By.CSS_SELECTOR, "# spawner_form > options:nth-child(2)")
        self.click_first_element_located(By.CSS_SELECTOR, "input.btn")
        self.click_first_element_located(By.ID, "start")

        self.wait_until_text_inside_element_located(
            By.CSS_SELECTOR, ".header", "APPLICATIONS")

    def tearDown(self):
        self.admin_logout()
        RemoteAppDriverTest.tearDown(self)
