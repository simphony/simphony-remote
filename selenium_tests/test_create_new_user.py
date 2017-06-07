from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By


class TestCreateNewUser(SeleniumTestBase):
    def test_cancel(self):
        with self.logged_in("admin"):
            self.click_element_located(By.LINK_TEXT, "Users")

            self.click_new_entry_button()

            self.click_cancel_button()

    def test_create_user(self):
        with self.logged_in("admin"):
            self.click_element_located(By.LINK_TEXT, "Users")

            self.click_new_entry_button()

            self.type_text_in_element_located(By.ID, "new-user-name", "mrenou")

            self.click_submit_button()
