# -*- coding: utf-8 -*-
import contextlib
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class AdminDriverTest(RemoteAppDriverTest):
    def click_new_entry_button(self):
        self.click_first_button("Create New Entry")

    def click_submit_button(self):
        self.click_first_button("Submit")
        self.wait_until_modal_closed()

    def click_ok_button(self):
        self.click_first_button("Ok")
        self.wait_until_modal_closed()

    def click_cancel_button(self):
        self.click_first_button("Cancel")
        self.wait_until_modal_closed()

    def _get_table_element(self, name):
        # Select row which contains somewhere the given name
        return self.driver.find_element_by_xpath(
            "//tr[td[text()='{}']]".format(name)
        )

    def trigger_row_action(self, row, action_name):
        # Select row
        row = self._get_table_element(row)
        # Get action button
        action_btn = row.find_element_by_xpath(
            "td/button[text()='{}']".format(action_name)
        )
        self.click_element(action_btn)

    @contextlib.contextmanager
    def logged_in(self):
        self.login("admin")
        try:
            yield
        finally:
            self.logout()
