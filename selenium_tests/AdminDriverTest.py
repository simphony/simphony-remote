# -*- coding: utf-8 -*-
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class AdminDriverTest(RemoteAppDriverTest):

    def admin_login(self):
        """ Login as an admin user. Handles both entering admin credentials
        and selecting appropriate Spawner options. We assume that if you
        use this routine, you are currently on the login page.
        """
        self.login("admin")

        self.click_first_element_located(By.ID, "start")
        self.click_first_element_located(By.CSS_SELECTOR, "input.btn")
        self.click_first_element_located(By.ID, "start")

    def admin_logout(self):
        """ Admin Logout. Ensures user session is stopped before performing logout.
        This action should be generally used whenever the Spawner options form is
        presented during logins so that it is correctly displayed for the next test
        runner.
        """
        self.driver.get(self.base_url + "/home")

        self.click_first_element_located(By.ID, "stop")
        self.click_first_element_located(By.ID, "logout")
        self.wait_until_text_inside_element_located(By.CSS_SELECTOR, "div.auth-form-header", "Sign in")

    def setUp(self):
        RemoteAppDriverTest.setUp(self)
        self.admin_login()

    def wait_until_visibility_of_row(self, row):
        """ Wait until a specific row is visible
        Parameters
        ----------
        row: String
            A string which permit to locate the row, it can be:
            - the index of the row ("2")
            - a user name ("JohnDoe")
            - an application name ("File Manager")
            - a container id ("3514azd65a4z4dazd131")

        Returns
        -------
        row_element: WebElement
            The row that you specified

        Example
        -------
        row_element = wait_until_visibility_of_row("JohnDoe")
        """
        return self.wait_until_presence_of_element_located(
            By.XPATH,
            "//tr[td[text()='{}']]".format(row)
        )

    def wait_until_invisibility_of_row(self, row):
        """ Wait until a specific row is invisible
        Parameters
        ----------
        row: String
            A string which permit to locate the row, it can be:
            - the index of the row ("2")
            - a user name ("JohnDoe")
            - an application name ("File Manager")
            - a container id ("3514azd65a4z4dazd131")

        Example
        -------
        wait_until_invisibility_of_row("JohnDoe")
        """
        self.wait_until_invisibility_of_element_located(
            By.XPATH,
            "//tr[td[text()='{}']]".format(row)
        )

    def click_row_action_button(self, row, action_name):
        """ Click on an action button in the datatable for a specific row
        Parameters
        ----------
        row: String
            A string which permit to locate the row, it can be:
            - the index of the row ("2")
            - a user name ("JohnDoe")
            - an application name ("File Manager")
            - a container id ("3514azd65a4z4dazd131")
        action_name: string
            The name of the action

        Example
        -------
        click_row_action_button("JohnDoe", "Remove")
        click_row_action_button("JohnDoe", "Policies")
        click_row_action_button("Mayavi", "Stop")
        """
        self.click_first_element_located(
            By.XPATH,
            "//tr[td[text()='{}']]/td/button[text()='{}']".format(
                row, action_name
            )
        )

    def tearDown(self):
        self.admin_logout()
        RemoteAppDriverTest.tearDown(self)
