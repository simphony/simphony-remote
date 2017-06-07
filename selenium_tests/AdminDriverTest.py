# -*- coding: utf-8 -*-
import contextlib
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class AdminDriverTest(RemoteAppDriverTest):
    def click_new_entry_button(self):
        self.click_element_located(By.ID, "global-action-0")

    def click_submit_button(self):
        self.click_element_located(By.ID, "modal-submit-btn")
        self.wait_until_modal_closed()

    def click_ok_button(self):
        self.click_element_located(By.ID, "modal-ok-btn")
        self.wait_until_modal_closed()

    def click_cancel_button(self):
        self.click_element_located(By.ID, "modal-cancel-btn")
        self.wait_until_modal_closed()

    def click_user_policies(self, index=0):
        self.click_element_located(By.ID, "row-{}-action-0".format(index))

    def click_remove_user(self, index=0):
        self.click_element_located(By.ID, "row-{}-action-1".format(index))

    @contextlib.contextmanager
    def logged_in(self):
        self.login("admin")
        try:
            yield
        finally:
            self.logout()
