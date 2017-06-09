# -*- coding: utf-8 -*-
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class AdminDriverTest(RemoteAppDriverTest):
    def setUp(self):
        RemoteAppDriverTest.setUp(self)
        self.login("admin")

    def click_new_entry_button(self):
        self.click_first_button("Create New Entry")

    def click_dialog_submit_button(self):
        self.click_first_button("Submit")
        self.wait_until_modal_closed()

    def click_dialog_ok_button(self):
        self.click_first_button("Ok")
        self.wait_until_modal_closed()

    def click_dialog_cancel_button(self):
        self.click_first_button("Cancel")
        self.wait_until_modal_closed()

    def trigger_row_action(self, row, action_name):
        self.click_first_element_located(
            By.XPATH,
            "//tr[td[text()='{}']]/td/button[text()='{}']".format(
                row, action_name
            )
        )

    def tearDown(self):
        self.logout()
        RemoteAppDriverTest.tearDown(self)
