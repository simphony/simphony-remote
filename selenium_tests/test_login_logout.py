# -*- coding: utf-8 -*-
from selenium_tests.selenium_test_base import SeleniumTestBase


class TestLoginLogout(SeleniumTestBase):
    def test_login_logout(self):
        driver = self.driver
        driver.get(self.base_url + "/hub/login")

        driver.find_element_by_id("username_input").clear()
        driver.find_element_by_id("username_input").send_keys("test")
        driver.find_element_by_id("password_input").clear()
        driver.find_element_by_id("password_input").send_keys("test")
        driver.find_element_by_id("login_submit").click()
        self.wait_for(
            lambda: "Available Applications" == driver.find_element_by_css_selector("h1").text
        )
        driver.find_element_by_id("logout").click()
        self.wait_for(
            lambda: "Sign in" == driver.find_element_by_css_selector("div.auth-form-header").text
        )
