# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
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

        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.ID, 'bnx_0')))

        driver.execute_script(
            "arguments[0].click()",
            driver.find_element_by_id("bnx_0")
        )
        self.wait_for(lambda: "noVNC" == driver.title)
        driver.execute_script(
            "arguments[0].click()",
            driver.find_element_by_link_text("Close")
            )
        self.wait_for(lambda: "noVNC" != driver.title)

        # Try clicking on View.
        driver.execute_script(
            "arguments[0].click()",
            driver.find_element_by_id("bnx_0")
        )
        self.wait_for(lambda: "noVNC" == driver.title)
        driver.execute_script(
            "arguments[0].click()",
            driver.find_element_by_link_text("Close")
            )

        # Click on Stop.
        self.wait_for(lambda: "noVNC" != driver.title)
        driver.execute_script(
            "arguments[0].click()",
            driver.find_element_by_id("bny_0")
        )
        self.wait_for(
            lambda: "Start" == driver.find_element_by_id("bnx_0").text)
        driver.find_element_by_id("logout").click()
