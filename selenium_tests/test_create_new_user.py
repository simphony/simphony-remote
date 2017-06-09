from selenium_tests.AdminDriverTest import AdminDriverTest
from selenium.webdriver.common.by import By


class TestCreateNewUser(AdminDriverTest):
    def test_cancel(self):
        self.click_first_element_located(By.LINK_TEXT, "Users")

        self.click_first_button("Create New Entry")
        self.click_modal_footer_button("Cancel")

    def test_create_and_remove_user(self):
        self.click_first_element_located(By.LINK_TEXT, "Users")

        self.click_first_button("Create New Entry")
        self.type_text_in_element_located(By.CSS_SELECTOR, ".modal-body > form > div > input", "mrenou")
        self.click_modal_footer_button("Submit")

        # Click remove button
        self.trigger_row_action("mrenou", "Remove")

        self.click_modal_footer_button("Ok")
