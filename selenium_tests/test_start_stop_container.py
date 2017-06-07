# -*- coding: utf-8 -*-
from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By


class TestContainerInteraction(SeleniumTestBase):
    def test_start_stop_container(self):
        with self.logged_in():
            self.wait_until_element_invisible(By.ID, "loading-spinner")

            self.select_application()

            self.click_element_located(By.ID, "start-button")

            self.wait_until_element_present(By.ID, "application")
            self.click_element_located(By.ID, "application-settings")
            self.click_element_located(By.ID, "stop-button")

    def test_focus(self):
        with self.running_container():
            iframe = self.wait_until_element_visible(By.TAG_NAME, "iframe")
            self.assertEqual(iframe, self.driver.switch_to.active_element)

            self.type_text_in_element_located(By.ID, "search-input", "")

            self.assertNotEqual(iframe, self.driver.switch_to.active_element)

            self.select_application()

            self.assertEqual(iframe, self.driver.switch_to.active_element)
