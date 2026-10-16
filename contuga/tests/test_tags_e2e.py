from django.contrib.staticfiles.testing import LiveServerTestCase
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from contuga.mixins import TestMixin
from contuga.tests.mixins.e2e_test_mixin import EndToEndTestMixin


class SeleniumTestCase(LiveServerTestCase, TestMixin, EndToEndTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user_email = "john.doe@example.com"
        self.user_password = "password"
        self.user = self.create_user(
            email=self.user_email,
            password=self.user_password,
        )

        self.tag = self.create_tag(name="Groceries")
        self.other_tag = self.create_tag(name="Travel")

    def test_tags_list_and_detail_page(self):
        self.selenium.get(self.live_server_url)
        self.login()

        self.selenium.get(f"{self.live_server_url}{reverse('tags:list')}")

        body = self.selenium.find_element(By.TAG_NAME, "body").text
        self.assertIn("Tags", body)
        self.assertIn(self.tag.name, body)
        self.assertIn(self.other_tag.name, body)

        link = self.selenium.find_element(By.LINK_TEXT, self.tag.name)
        link.click()

        self.assertEqual(
            self.selenium.find_element(By.TAG_NAME, "h1").text,
            "Tag details",
        )
        self.assertIn(self.tag.name, self.selenium.page_source)

    def test_tag_create_and_delete(self):
        self.selenium.get(self.live_server_url)
        self.login()

        self.selenium.get(f"{self.live_server_url}{reverse('tags:create')}")
        self.selenium.find_element(By.NAME, "name").send_keys("Weekend")
        self.selenium.find_element(By.XPATH, '//button[contains(text(), "Save")]').click()

        self.assertEqual(
            self.selenium.find_element(By.TAG_NAME, "h1").text,
            "Tag details",
        )
        self.assertIn("Weekend", self.selenium.page_source)

        self.selenium.find_element(By.LINK_TEXT, "Delete").click()
        self.selenium.find_element(By.XPATH, '//button[contains(text(), "Confirm")]').click()

        self.assertNotIn("Weekend", self.selenium.page_source)
