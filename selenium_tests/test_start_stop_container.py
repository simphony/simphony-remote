# -*- coding: utf-8 -*-
from selenium.webdriver.common.action_chains import ActionChains
from selenium_tests.selenium_test_base import SeleniumTestBase


class TestContainerInteraction(SeleniumTestBase):
    def test_start_stop_container(self):
        driver = self.driver
        with self.login():
            self.wait_for(lambda:
                driver.find_element_by_css_selector(
                    "#applistentries > li > a > span").text != "Loading")

            self.click_by_css_selector("#applistentries > li > a > img")
            self.click_by_css_selector(".start-button")

            driver.find_element_by_id("application")
            ActionChains(driver).move_to_element(
                driver.find_element_by_css_selector(
                    "#applistentries .app-icon")
                ).click(driver.find_element_by_css_selector(".stop-button")
            ).perform()

    def test_focus(self):
        driver = self.driver
        with self.running_container():
            iframe = driver.find_element_by_css_selector("iframe")
            self.assertEqual(iframe, self.driver.switch_to.active_element)

            search_box = driver.find_element_by_css_selector(
                "input.form-control")
            ActionChains(driver).move_to_element(search_box).click().perform()

            self.assertNotEqual(iframe, self.driver.switch_to.active_element)

            self.click_by_css_selector("#applistentries > li > a > img")

            self.assertEqual(iframe, self.driver.switch_to.active_element)
