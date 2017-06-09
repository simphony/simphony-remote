from selenium_tests.AdminDriverTest import AdminDriverTest
from selenium.webdriver.common.by import By


class TestAdminNameHeaderBug(AdminDriverTest):
    def test_admin_name_header_bug(self):
        self.click_first_element_located(By.LINK_TEXT, "Users")

        self.click_row_action_button("test", "Policies")

        self.wait_until_text_inside_element_located(By.CSS_SELECTOR, "span.hidden-xs", "admin")
