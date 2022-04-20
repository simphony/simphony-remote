# -*- coding: utf-8 -*-
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class TestSpawnerOptionsForm(RemoteAppDriverTest):

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
            By.CSS_SELECTOR, "#session_form > option:nth-child(2)")
        self.click_first_element_located(By.CSS_SELECTOR, "input.btn")
        self.click_first_element_located(By.ID, "start")

        self.wait_until_text_inside_element_located(
            By.CSS_SELECTOR, ".header", "APPLICATIONS")

    def tearDown(self):
        self.logout()
        RemoteAppDriverTest.tearDown(self)
