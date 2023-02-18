from django.urls import reverse
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from contuga.contrib.transactions import constants as transaction_constants


class TransactionFormPageMixin:
    def navigate_to_transaction_update_page(self, transaction):
        current_url = self.selenium.current_url

        table = self.selenium.find_element_by_id("transactions")
        tbody = table.find_element_by_tag_name("tbody")
        update_url = reverse("transactions:update", kwargs={"pk": transaction.pk})

        link = tbody.find_element_by_xpath(f"//a[@href='{update_url}']")
        link.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def navigate_to_transaction_create_page(self):
        current_url = self.selenium.current_url

        navigation = self.selenium.find_element_by_tag_name("nav")
        transaction_section = navigation.find_element_by_link_text("Transactions")
        transaction_section.click()

        transaction_create_page_link = (
            transaction_section.parent.find_element_by_link_text("Add new")
        )
        transaction_create_page_link.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def fill_transaction_form(
        self,
        type,
        amount,
        account_name,
        category_name,
        description,
        tags,
        should_clear_inputs=False,
        should_clear_tags=False,
    ):
        form = self.selenium.find_element_by_xpath("//main/div/div/form")

        type_input = Select(form.find_element_by_name("type"))
        type_input.select_by_visible_text(type)

        amount_input = form.find_element_by_name("amount")

        if should_clear_inputs:
            amount_input.clear()

        amount_input.send_keys(amount)

        account_input = Select(form.find_element_by_name("account"))
        account_input.select_by_visible_text(account_name)

        category_input = Select(form.find_element_by_name("category"))
        category_input.select_by_visible_text(category_name)

        if should_clear_tags:
            existing_tag_elements = form.find_elements_by_tag_name("tag")

            for existing_tag_element in existing_tag_elements:
                existing_tag_element.find_element_by_tag_name("x").click()

        tags_input = form.find_element_by_class_name("tagify__input")
        tags_label = self.selenium.find_element_by_xpath(
            '//label[contains(text(), "Tags")]'
        )

        for tag in tags:
            tags_input.send_keys(tag)
            tags_label.click()

        description_input = form.find_element_by_name("description")

        if should_clear_inputs:
            description_input.clear()

        description_input.send_keys(description)

    def submit_transaction_form(self, button_text="Save"):
        current_url = self.selenium.current_url

        button = self.selenium.find_element_by_xpath(
            f"//button[contains(text(), '{button_text}')]"
        )
        button.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def verify_transaction_type_input(self, input, type):
        selected_option = input.all_selected_options[0]

        self.assertEqual(selected_option.get_attribute("value"), type)

        if type == transaction_constants.INCOME:
            self.assertEqual(selected_option.text, "Income")
        else:
            self.assertEqual(selected_option.text, "Expenditure")

    def verify_no_category_is_selected(self, input):
        self.verify_category_input(
            input=input, expected_value="", expected_label="---------"
        )

    def verify_category_input(
        self, input, expected_value=None, expected_label=None, category=None
    ):
        if category:
            expected_value = str(category.pk)
            expected_label = category.name

        selected_option = input.all_selected_options[0]

        self.assertEqual(selected_option.get_attribute("value"), expected_value)
        self.assertEqual(selected_option.text, expected_label)

    def verify_category_options(self, input, expected_options):
        options = [
            (option.get_attribute("value"), option.text) for option in input.options
        ]
        self.assertEqual(options, expected_options)
