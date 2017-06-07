from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By


class TestCreateNewUser(SeleniumTestBase):
    def test_cancel(self):
        with self.logged_in("admin"):
            self.click_element_located(By.LINK_TEXT, "Users")

            self.click_new_entry_button()

            self.cancel_modal()
