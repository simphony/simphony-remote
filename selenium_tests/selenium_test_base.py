# -*- coding: utf-8 -*-
import time
import os
import contextlib
import sqlite3
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
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
        self.wait = WebDriverWait(self.driver, 30)
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

    def wait_until_element_present(self, how, what):
        return self.wait.until(EC.presence_of_element_located((how, what)))

    def wait_until_alert_present(self):
        return self.wait.until(EC.alert_is_present)

    def wait_until_text_inside(self, how, what, text):
        return self.wait.until(EC.text_to_be_present_in_element((how, what), text))

    def wait_until_element_visible(self, how, what):
        return self.wait.until(EC.visibility_of_element_located((how, what)))

    def wait_until_element_invisible(self, how, what):
        return self.wait.until(EC.invisibility_of_element_located((how, what)))

    def wait_until_element_clickable(self, how, what):
        return self.wait.until(EC.element_to_be_clickable((how, what)))

    def click_element_located(self, how, what):
        element = self.wait_until_element_clickable(how, what)
        element.click()

    def type_text_in_element_located(self, how, what, text):
        element = self.wait_until_element_clickable(how, what)
        element.clear()
        element.send_keys(text)

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

    def login(self, username="test"):
        self.driver.get(self.base_url + "/hub/login")

        self.type_text_in_element_located(By.ID, "username_input", username)
        self.type_text_in_element_located(By.ID, "password_input", username)

        self.click_element_located(By.ID, "login_submit")

    def logout(self):
        self.click_element_located(By.CLASS_NAME, "user-menu")
        self.click_element_located(By.ID, "logout")
        self.wait_until_text_inside(By.CSS_SELECTOR, "div.auth-form-header", "Sign in")

    @contextlib.contextmanager
    def logged_in(self, username="test"):
        self.login(username)

        try:
            yield
        finally:
            self.logout()

    @contextlib.contextmanager
    def running_container(self):
        with self.logged_in():
            driver = self.driver
            self.wait_until_element_invisible(By.ID, "loading-spinner")

            self.click_element_located(By.CSS_SELECTOR, "#applistentries > li > a > img")
            self.click_element_located(By.CLASS_NAME, "start-button")

            try:
                yield
            finally:
                self.wait_until_element_present(By.ID, "application")
                self.click_element_located(By.CSS_SELECTOR, ".dropdown > a > img")
                self.click_element_located(By.ID, "stop-button")
