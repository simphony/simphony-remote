from selenium_tests.selenium_test_base import SeleniumTestBase
from selenium.webdriver.common.by import By


class TestAdminNameHeaderBug(SeleniumTestBase):
    def test_admin_name_header_bug(self):
        driver = self.driver
        with self.logged_in("admin"):
            self.click_element_located(By.LINK_TEXT, "Users")

            self.click_button("Policies")

            self.wait_until_text_inside(By.CSS_SELECTOR, "span.hidden-xs", "admin")
