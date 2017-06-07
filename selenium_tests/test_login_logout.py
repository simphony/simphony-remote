# -*- coding: utf-8 -*-
from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By


class TestLoginLogout(SeleniumTestBase):
    def test_login_logout(self):
        self.login("test")

        self.wait_until_element_visible(By.ID, "applistentries")

        self.logout()
