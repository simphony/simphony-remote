# -*- coding: utf-8 -*-
import time
import os
import contextlib
import sqlite3
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains
import unittest


class SeleniumTestBase(unittest.TestCase):
    def setUp(self):
        ff_binary = webdriver.firefox.firefox_binary.FirefoxBinary()
        ff_profile = webdriver.firefox.firefox_profile.FirefoxProfile()
        ff_profile.assume_untrusted_cert_issuer = True
        ff_profile.accept_untrusted_certs = True
        capabilities = webdriver.DesiredCapabilities().FIREFOX
        capabilities['acceptSslCerts'] = True
        self.driver = webdriver.Firefox(firefox_binary=ff_binary,
                                        firefox_profile=ff_profile,
                                        capabilities=capabilities,
                                        timeout=60)
        self.driver.implicitly_wait(30)
        self.base_url = "https://127.0.0.1:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True

        permissions_db_path = os.path.join(ff_profile.profile_dir,
                                           "permissions.sqlite")

        with contextlib.closing(sqlite3.connect(permissions_db_path)) as db:
            cur = db.cursor()
            cur.execute(
                ("INSERT INTO moz_perms VALUES (1, '{base_url}', "
                 "'popup', 1, 0, 0, 1474977124357)").format(
                    base_url=self.base_url))
            db.commit()

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

    def wait_for(self, check_func, timeout=30):
        for i in range(timeout):
            try:
                if check_func():
                    break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")

    def click_by_css_selector(self, css_selector):
        # Workaround for some unexpected behavior with clicking some elements.
        self.driver.execute_script(
            "arguments[0].click()",
            self.driver.find_element_by_css_selector(css_selector))

    def click_button(self, button_text, number=0):
        """
        Clicks a button with a given text.

        Parameters
        ----------
        button_text: str
            The text of the button
        number: int
            If multiple buttons with the same label are found, click
            the number-th (zero based). If not specified, the first (0th)
            button will be clicked.
        """
        self.wait_for(
            lambda: len(self.get_buttons_by_text(button_text)) > number)

        button = self.get_buttons_by_text(button_text)[number]
        self.driver.execute_script("arguments[0].click()", button)

    def get_buttons_by_text(self, text):
        return [button for button in self.driver.find_elements_by_tag_name("button")
                if button.text == text]

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    @contextlib.contextmanager
    def login(self, username="test"):
        driver = self.driver
        driver.get(self.base_url + "/hub/login")

        driver.find_element_by_id("username_input").clear()
        driver.find_element_by_id("username_input").send_keys(username)
        driver.find_element_by_id("password_input").clear()
        driver.find_element_by_id("password_input").send_keys(username)
        driver.find_element_by_id("login_submit").click()

        try:
            yield
        finally:
            driver.find_element_by_css_selector(".dropdown-toggle").click()
            driver.find_element_by_id("logout").click()
            self.wait_for(
                lambda: "Sign in" == driver.find_element_by_css_selector(
                    "div.auth-form-header").text
            )

    @contextlib.contextmanager
    def running_container(self):
        with self.login():
            driver = self.driver
            self.wait_for(lambda:
                          driver.find_element_by_css_selector(
                              "#applist > li > a").text != "Loading")

            self.click_by_css_selector("#applist > li > a")
            self.click_by_css_selector(".start-button")

            try:
                yield
            finally:
                driver.find_element_by_id("application")
                ActionChains(driver).move_to_element(
                    driver.find_element_by_css_selector("#applist .app-icon")
                ).click(driver.find_element_by_css_selector(".stop-button")
                        ).perform()
