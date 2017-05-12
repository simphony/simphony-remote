# -*- coding: utf-8 -*-
from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By


class TestHideApplication(SeleniumTestBase):
    def test_hide_application(self):
        driver = self.driver
        with self.login():
            self.wait_for(lambda:
                          driver.find_element_by_css_selector(
                              "#loading-spinner").value_of_css_property(
                              'display') == "none")

            # Click on the search box
            search_box = driver.find_element_by_name("q")
            search_box.clear()
            search_box.send_keys('foobarheho')

            self.wait_for(lambda:
                          not self.is_element_present(
                              By.CSS_SELECTOR, '#applistentries > li'))
