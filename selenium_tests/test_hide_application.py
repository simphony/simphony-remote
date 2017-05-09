# -*- coding: utf-8 -*-
from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

            WebDriverWait(driver, 3).until(
                EC.invisibility_of_element_located((
                    By.CSS_SELECTOR, '#applistentries > li')))

            self.assertFalse(self.is_element_present(
                By.CSS_SELECTOR, '#applistentries > li'))
