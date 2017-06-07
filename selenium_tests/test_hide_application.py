# -*- coding: utf-8 -*-
from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By


class TestHideApplication(SeleniumTestBase):
    def test_hide_application(self):
        with self.logged_in():
            self.wait_until_application_list_loaded()

            self.type_text_in_element_located(By.ID, "search-input", "foobarheho")

            self.wait_until_text_inside(By.ID, "applistentries", "")
