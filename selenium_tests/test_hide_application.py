# -*- coding: utf-8 -*-
from selenium_tests.UserDriverTest import UserDriverTest
from selenium.webdriver.common.by import By


class TestHideApplication(UserDriverTest):
    def test_hide_application(self):
        with self.logged_in():
            self.wait_until_application_list_loaded()

            self.type_text_in_element_located(By.ID, "search-input", "foobarheho")

            self.wait_until_text_inside(By.ID, "applistentries", "")
