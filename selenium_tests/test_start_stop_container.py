# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest
import time
import re


class TestStartStopContainer(unittest.TestCase):

    def setUp(self):
        ff_binary = webdriver.firefox.firefox_binary.FirefoxBinary()
        ff_profile = webdriver.firefox.firefox_profile.FirefoxProfile()
        ff_profile.assume_untrusted_cert_issuer = True
        ff_profile.accept_untrusted_certs = True
        capabilities = webdriver.DesiredCapabilities().FIREFOX
        capabilities['acceptSslCerts'] = True
        self.driver = webdriver.Firefox(firefox_binary=ff_binary,
                                        firefox_profile=ff_profile,
                                        capabilities=capabilities)
        self.driver.implicitly_wait(30)
        self.base_url = "https://127.0.0.1:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True

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
        driver.save_screenshot("shot.png")
        driver.find_element_by_link_text("Close").click()
        driver.find_element_by_name("action").click()
        for i in range(60):
            print(driver.title)
            try:
                if "noVNC" == driver.title:
                    break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        driver.find_element_by_xpath("//i").click()
        driver.find_element_by_xpath("(//button[@name='action'])[2]").click()
        for i in range(60):
            try:
                if "Start" == driver.find_element_by_name("action").text:
                    break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        driver.find_element_by_id("logout").click()

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
