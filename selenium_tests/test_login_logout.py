# -*- coding: utf-8 -*-
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class TestLoginLogout(RemoteAppDriverTest):
    def test_login_logout(self):
        self.login("test")

        self.wait_until_visibility_of_element_located(By.ID, "applistentries")

        self.logout()
