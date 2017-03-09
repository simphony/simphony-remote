from selenium_tests.selenium_test_base import SeleniumTestBase


class TestAdminNameHeaderBug(SeleniumTestBase):
    def test_admin_name_header_bug(self):
        driver = self.driver
        with self.login("admin"):
            print("hello")
            driver.find_element_by_link_text("Users").click()
            driver.find_element_by_link_text("Show").click()
            self.wait_for(lambda:
                "admin" == driver.find_element_by_css_selector(
                    "span.hidden-xs").text
            )
