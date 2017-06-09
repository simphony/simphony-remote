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


class RemoteAppDriverTest(unittest.TestCase):
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

    def wait_until_presence_of_element_located(self, how, what):
        return self.wait.until(EC.presence_of_element_located((how, what)))

    def wait_until_text_inside_element_located(self, how, what, text):
        return self.wait.until(EC.text_to_be_present_in_element((how, what), text))

    def wait_until_visibility_of_element_located(self, how, what):
        return self.wait.until(EC.visibility_of_element_located((how, what)))

    def wait_until_visibility_of(self, element):
        return self.wait.until(EC.visibility_of(element))

    def wait_until_invisibility_of_element_located(self, how, what):
        return self.wait.until(EC.invisibility_of_element_located((how, what)))

    def wait_until_clickability_of_element_located(self, how, what):
        return self.wait.until(EC.element_to_be_clickable((how, what)))

    def click_first_element_located(self, how, what):
        element = self.wait_until_clickability_of_element_located(how, what)
        element.click()

    def click_first_button(self, name):
        self.click_first_element_located(
            By.XPATH, "//button[text()='{}']".format(name)
        )

    def type_text_in_element_located(self, how, what, text):
        element = self.wait_until_clickability_of_element_located(how, what)
        element.clear()
        element.send_keys(text)

    def wait_until_modal_closed(self):
        return self.wait.until_not(EC.alert_is_present())

    def click_modal_footer_button(self, name):
        self.click_first_element_located(
            By.XPATH, "//div[contains(@class,'modal-footer')]/button[text()='{}']".format(name)
        )
        self.wait_until_modal_closed()

    def login(self, username="test"):
        self.driver.get(self.base_url + "/hub/login")

        self.type_text_in_element_located(By.ID, "username_input", username)
        self.type_text_in_element_located(By.ID, "password_input", username)

        self.click_first_element_located(By.ID, "login_submit")

    def logout(self):
        self.click_first_element_located(By.ID, "user-menu")
        self.click_first_element_located(By.ID, "logout")
        self.wait_until_text_inside_element_located(By.CSS_SELECTOR, "div.auth-form-header", "Sign in")

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
