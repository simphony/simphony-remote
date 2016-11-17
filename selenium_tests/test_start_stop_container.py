# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.support import expected_conditions as EC


class TestStartStopContainer(SeleniumTestBase):
    def test_start_stop_container(self):
        driver = self.driver
        driver.get(self.base_url + "/hub/login")
        driver.find_element_by_id("username_input").clear()
        driver.find_element_by_id("username_input").send_keys("test")
        driver.find_element_by_id("password_input").clear()
        driver.find_element_by_id("password_input").send_keys("test")
        driver.find_element_by_id("login_submit").click()

        self.wait_for(lambda:
            driver.find_element_by_css_selector("#applist > li > a").text !=
            "Loading")

        self.click_by_css_selector("#applist > li > a")
        self.click_by_css_selector(".start-button")

        driver.find_element_by_id("application")
        ActionChains(driver).move_to_element(
            driver.find_element_by_css_selector("#applist .app-icon")
            ).click(driver.find_element_by_css_selector(".stop-button")
            ).perform()

        driver.find_element_by_css_selector(".dropdown-toggle").click()
        driver.find_element_by_id("logout").click()
