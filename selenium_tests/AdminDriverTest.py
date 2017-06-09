# -*- coding: utf-8 -*-
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class AdminDriverTest(RemoteAppDriverTest):
    def setUp(self):
        RemoteAppDriverTest.setUp(self)
        self.login("admin")

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
        self.logout()
        RemoteAppDriverTest.tearDown(self)
