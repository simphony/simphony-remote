from selenium_tests.selenium_test_base import SeleniumTestBase


class TestAdminNameHeaderBug(SeleniumTestBase):
    def test_admin_name_header_bug(self):
        driver = self.driver
        with self.login("admin"):
            driver.find_element_by_link_text("Users").click()
            self.click_button("Policies")
            self.wait_for(lambda:
                "admin" == driver.find_element_by_css_selector(
                    "span.hidden-xs").text
            )
