# -*- coding: utf-8 -*-
from selenium.webdriver.common.action_chains import ActionChains
from selenium_tests.selenium_test_base import SeleniumTestBase


class TestContainerInteraction(SeleniumTestBase):
    def test_start_stop_container(self):
        driver = self.driver
        with self.login():
            self.wait_for(lambda:
                driver.find_element_by_css_selector(
                    "#applist > li > a").text != "Loading")

            self.click_by_css_selector("#applist > li > a")
            self.click_by_css_selector(".start-button")

            driver.find_element_by_id("application")
            ActionChains(driver).move_to_element(
                driver.find_element_by_css_selector("#applist .app-icon")
                ).click(driver.find_element_by_css_selector(".stop-button")
            ).perform()
