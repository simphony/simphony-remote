# -*- coding: utf-8 -*-
from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By


class TestHideApplication(SeleniumTestBase):
    def test_hide_application(self):
        driver = self.driver
        with self.logged_in():
            self.wait_until_element_invisible(By.ID, "loading-spinner")

            # Click on the search box
            search_box = driver.find_element_by_name("q")
            search_box.clear()
            search_box.send_keys('foobarheho')

            self.wait_until_text_inside(By.ID, "applistentries", "")
