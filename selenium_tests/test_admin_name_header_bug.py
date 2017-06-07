from selenium_tests.AdminDriverTest import AdminDriverTest
from selenium.webdriver.common.by import By


class TestAdminNameHeaderBug(AdminDriverTest):
    def test_admin_name_header_bug(self):
        with self.logged_in():
            self.click_element_located(By.LINK_TEXT, "Users")

            self.click_user_policies(0)

            self.wait_until_text_inside(By.CSS_SELECTOR, "span.hidden-xs", "admin")
