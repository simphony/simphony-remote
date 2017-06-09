# -*- coding: utf-8 -*-
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class AdminDriverTest(RemoteAppDriverTest):
    def setUp(self):
        RemoteAppDriverTest.setUp(self)
        self.login("admin")

    def click_row_action_button(self, row, action_name):
        self.click_first_element_located(
            By.XPATH,
            "//tr[td[text()='{}']]/td/button[text()='{}']".format(
                row, action_name
            )
        )

    def tearDown(self):
        self.logout()
        RemoteAppDriverTest.tearDown(self)
