from selenium_tests.AdminDriverTest import AdminDriverTest
from selenium.webdriver.common.by import By
import os


class TestUserAccounting(AdminDriverTest):
    def test_create_new_entry_button(self):
        self.click_first_element_located(By.LINK_TEXT, "Users")

        self.click_first_button("Create New Entry")
        self.click_modal_footer_button("Cancel")

    def test_create_and_remove_user(self):
        self.click_first_element_located(By.LINK_TEXT, "Users")

        self.click_first_button("Create New Entry")
        self.type_text_in_element_located(By.CSS_SELECTOR, ".modal-body > form > div > input", "mrenou")
        self.click_modal_footer_button("Submit")

        # Click remove button
        self.click_row_action_button("mrenou", "Remove")

        self.click_modal_footer_button("Ok")

        self.wait_until_invisibility_of_row("mrenou")

    def test_admin_name_header_bug(self):
        self.click_first_element_located(By.LINK_TEXT, "Users")

        self.click_row_action_button("test", "Policies")

        self.wait_until_text_inside_element_located(By.CSS_SELECTOR, "span.hidden-xs", "admin")

    def test_user_id(self):
        self.click_first_element_located(By.LINK_TEXT, "Users")

        self.click_row_action_button("test", "Policies")

        self.wait_until_visibility_of_row("simphonyproject/simphonic-mayavi")

        self.driver.get(os.path.join(
            self.base_url,
            "user/admin/#/users/36/accounting"
        ))

        self.wait_until_presence_of_element_located(By.CSS_SELECTOR, "div.alert-danger")
        self.wait_until_invisibility_of_row("simphonyproject/simphonic-mayavi")
