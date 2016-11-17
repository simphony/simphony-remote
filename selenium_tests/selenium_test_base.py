# -*- coding: utf-8 -*-
import time
import os
import contextlib
import sqlite3
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
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

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
