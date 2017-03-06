from selenium_tests.selenium_test_base import SeleniumTestBase


class TestAdminNameHeaderBug(SeleniumTestBase):
    def test_admin_name_header_bug(self):
        driver = self.driver
        driver.get(self.base_url + "/hub/login")
        driver.find_element_by_id("username_input").clear()
        driver.find_element_by_id("username_input").send_keys("admin")
        driver.find_element_by_id("password_input").clear()
        driver.find_element_by_id("password_input").send_keys("admin")
        driver.find_element_by_id("login_submit").click()
        driver.find_element_by_link_text("Users").click()
        driver.find_element_by_link_text("Show").click()
        self.wait_for(lambda:
            "admin" == driver.find_element_by_css_selector(
                "span.hidden-xs").text
        )
        driver.find_element_by_css_selector("span.hidden-xs").click()
        driver.find_element_by_css_selector("i.fa.fa-sign-out").click()
        driver.find_element_by_id("password_input").clear()
        driver.find_element_by_id("password_input").send_keys("admin")

if __name__ == "__main__":
    unittest.main()
