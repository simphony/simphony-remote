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
        """ Wait until a located element is present
        Parameters
        ----------
        how: String
            How you want to locate the element. See selenium.webdriver.common.by
        what: String
            What you want to locate.

        Returns:
        --------
        element:
            The element founded

        Example:
        --------
        start_button = wait_until_presence_of_element_located(
            By.ID, "start-button")
        iframe = wait_until_presence_of_element_located(By.TAG_NAME, "iframe")
        """
        return self.wait.until(EC.presence_of_element_located((how, what)))

    def wait_until_text_inside_element_located(self, how, what, text):
        """ Wait until a located element contains some text
        Parameters
        ----------
        how: String
            How you want to locate the element. See selenium.webdriver.common.by
        what: String
            What you want to locate.
        text: String
            The text which must be contained by the located element

        Returns:
        --------
        element:
            The element founded

        Example:
        --------
        conclusion_title = wait_until_text_inside_element_located(
            By.TAG_NAME, "h3", "Conclusion")
        """
        return self.wait.until(EC.text_to_be_present_in_element((how, what), text))

    def wait_until_visibility_of_element_located(self, how, what):
        """ Wait until a located element is visible, which means that it's rendered and
        the CSS display style is not "none".
        Parameters
        ----------
        how: String
            How you want to locate the element. See selenium.webdriver.common.by
        what: String
            What you want to locate.

        Returns:
        --------
        element:
            The element founded

        Example:
        --------
        button = wait_until_visibility_of_element_located(By.TAG_NAME, "button")
        """
        return self.wait.until(EC.visibility_of_element_located((how, what)))

    def wait_until_visibility_of(self, element):
        """ Wait until an element is visible, which means that it's rendered and
        the CSS display style is not "none".
        Parameters
        ----------
        element: WebElement
            The web element which is supposed to be visible

        Returns:
        --------
        element:
            The element

        Example:
        --------
        wait_until_visibility_of(my_button)
        """
        return self.wait.until(EC.visibility_of(element))

    def wait_until_invisibility_of_element_located(self, how, what):
        """ Wait until an element is invisible, which means that it's not rendered or
        the CSS display style is "none".
        Parameters
        ----------
        how: String
            How you want to locate the element. See selenium.webdriver.common.by
        what: String
            What you want to locate.

        Returns:
        --------
        element:
            The element founded

        Example:
        --------
        button = wait_until_invisibility_of_element_located(By.TAG_NAME, "button")
        """
        return self.wait.until(EC.invisibility_of_element_located((how, what)))

    def wait_until_clickability_of_element_located(self, how, what):
        """ Wait until an element is clickable, which means that it's visible,
        enabled and nothing is above this element.
        Parameters
        ----------
        how: String
            How you want to locate the element. See selenium.webdriver.common.by
        what: String
            What you want to locate.

        Returns:
        --------
        element:
            The element founded

        Example:
        --------
        button = wait_until_clickability_of_element_located(By.TAG_NAME, "button")
        button.click()
        """
        return self.wait.until(EC.element_to_be_clickable((how, what)))

    def click_first_element_located(self, how, what):
        """ Wait until an element is clickable and click it
        Parameters
        ----------
        how: String
            How you want to locate the element. See selenium.webdriver.common.by
        what: String
            What you want to locate.

        Example:
        --------
        click_first_element_located(By.TAG_NAME, "button")
        """
        element = self.wait_until_clickability_of_element_located(how, what)
        element.click()

    def click_first_button(self, name):
        """ Click the first founded button containing a given name. If the button
        is not clickable, it will wait until it is and then click it.
        Parameters
        ----------
        name: String
            The name of the button you want to click

        Example:
        --------
        click_first_button("Ok")
        click_first_button("Remove")
        """
        self.click_first_element_located(
            By.XPATH, "//button[text()='{}']".format(name)
        )

    def type_text_in_element_located(self, how, what, text):
        """ Type text into an located element.
        Parameters
        ----------
        how: String
            How you want to locate the element. See selenium.webdriver.common.by
        what: String
            What you want to locate.
        text: String
            The text that you want to type in the element

        Example:
        --------
            type_text_in_element_located(By.TAG_NAME, "input", "Hello World!")
        """
        element = self.wait_until_clickability_of_element_located(how, what)
        element.clear()
        element.send_keys(text)

    def wait_until_modal_closed(self):
        """ Wait until the modal dialog is closed. We assume here that only
        one modal dialog/alert dialog can be opened at the same time.
        Returns
        -------
        element: WebElement
            The modal dialog
        """
        return self.wait.until_not(EC.alert_is_present())

    def click_modal_footer_button(self, name):
        """ Click the first founded button containing a given name in the modal
        footer and then wait until the modal dialog is closed. We assume here
        that only one modal dialog can be opened at the same time and that it
        contains a footer with buttons. We also assume that whatever the button
        does, it will close the modal dialog.
        Parameters
        ----------
        name: String
            The name of the button you want to click

        Example:
        --------
        click_modal_footer_button("Ok")
        click_modal_footer_button("Submit")
        click_modal_footer_button("Cancel")
        """
        self.click_first_element_located(
            By.XPATH, "//div[contains(@class,'modal-footer')]/button[text()='{}']".format(name)
        )
        self.wait_until_modal_closed()

    def login(self, username="test"):
        """ Login as a given user name. We assume that if you use this routine,
        you are currently on the login page.
        Parameters
        ----------
        username: String
            The name of the user, it can be "admin" if you want to login as admin.

        Example:
        --------
        login("JohnDoe")
        login("admin")
        """
        self.driver.get(self.base_url + "/hub/login")

        self.type_text_in_element_located(By.ID, "username_input", username)
        self.type_text_in_element_located(By.ID, "password_input", username)

        self.click_first_element_located(By.ID, "login_submit")

    def logout(self):
        """ Logout. We assume that if you use this routine you are currently on
        the main page, and that the user-menu is clickable (which means that
        there is no modal dialog in front of it).
        """
        self.click_first_element_located(By.ID, "user-menu")
        self.click_first_element_located(By.ID, "logout")
        self.wait_until_text_inside_element_located(By.CSS_SELECTOR, "div.auth-form-header", "Sign in")

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
