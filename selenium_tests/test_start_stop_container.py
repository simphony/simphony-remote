# -*- coding: utf-8 -*-
from selenium.webdriver.common.action_chains import ActionChains
from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By


class TestContainerInteraction(SeleniumTestBase):
    def test_start_stop_container(self):
        driver = self.driver
        with self.logged_in():
            self.wait_until_element_invisible(By.ID, "loading-spinner")

            self.click_element_located(By.CSS_SELECTOR, "#applistentries > li > a > img")
            self.click_element_located(By.CLASS_NAME, "start-button")

            self.wait_until_element_present(By.ID, "application")
            self.click_element_located(By.CSS_SELECTOR, ".dropdown > a > img")
            self.click_element_located(By.ID, "stop-button")

    def test_focus(self):
        driver = self.driver
        with self.running_container():
            iframe = driver.find_element_by_css_selector("iframe")
            self.assertEqual(iframe, self.driver.switch_to.active_element)

            search_box = driver.find_element_by_css_selector(
                "input.form-control")
            ActionChains(driver).move_to_element(search_box).click().perform()

            self.assertNotEqual(iframe, self.driver.switch_to.active_element)

            self.click_element_located(By.CSS_SELECTOR, "#applistentries > li > a > img")

            self.assertEqual(iframe, self.driver.switch_to.active_element)
