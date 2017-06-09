# -*- coding: utf-8 -*-
from selenium_tests.UserDriverTest import UserDriverTest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class TestShareApplication(UserDriverTest):
    def test_share_modal(self):
        with self.running_container():
            self.open_application_settings()

            self.click_first_element_located(By.ID, "share-button")

            self.click_modal_footer_button("Close")

    def test_share_button(self):
        with self.running_container():
            self.open_application_settings()

            self.click_first_element_located(By.ID, "share-button")

            self.click_first_element_located(By.ID, "cp-clipboard-button")

            # Now the share url should be in the clipboard
            input_element = self.driver.find_element_by_id("shared-url")

            # Clear the input element and paste what is in the clipboard in
            # order to retrieve it (lacking better way to retrieve the clipboard
            # value)
            input_element.clear()
            input_element.send_keys(Keys.CONTROL, 'v')
            clipboard_value = input_element.get_attribute("value")

            # Go to the shared url
            self.driver.get(clipboard_value)
            self.wait_until_presence_of_element_located(By.ID, "noVNC_screen")

            # Go back to simphony-remote
            self.driver.back()
            self.wait_until_application_list_loaded()
