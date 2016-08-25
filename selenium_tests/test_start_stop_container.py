# -*- coding: utf-8 -*-
import unittest
import time

from selenium_tests.selenium_test_base import SeleniumTestBase


class TestStartStopContainer(SeleniumTestBase):
    def test_start_stop_container(self):
        driver = self.driver
        driver.get(self.base_url + "/hub/login")
        driver.find_element_by_id("username_input").clear()
        driver.find_element_by_id("username_input").send_keys("test")
        driver.find_element_by_id("password_input").clear()
        driver.find_element_by_id("password_input").send_keys("test")
        driver.find_element_by_id("login_submit").click()
        driver.find_element_by_name("action").click()
        for i in range(60):
            try:
                if "noVNC" == driver.title:
                    break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        driver.find_element_by_link_text("Close").click()
        for i in range(60):
            print(driver.title)
            time.sleep(1)
        driver.find_element_by_name("action").click()
        self.wait_for(lambda: "noVNC" == driver.title)
        driver.find_element_by_xpath("//i").click()
        driver.find_element_by_xpath("(//button[@name='action'])[2]").click()
        self.wait_for(
            lambda: "Start" == driver.find_element_by_name("action").text)
        driver.find_element_by_id("logout").click()
