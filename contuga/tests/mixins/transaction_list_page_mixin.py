from django.utils import formats


class TransactionListPageMixin:
    def verify_transaction_list(self, transactions):
        table = self.selenium.find_element_by_id("transactions")
        tbody = table.find_element_by_tag_name("tbody")
        rows = tbody.find_elements_by_tag_name("tr")

        for index, transaction in enumerate(transactions):
            with self.subTest(row_index=index):
                row = rows[index]
                columns = row.find_elements_by_tag_name("td")

                self.verify_amount(columns, transaction)
                self.verify_account(columns, transaction)
                self.verify_category(columns, transaction)
                self.verify_tags(columns, transaction)
                self.verify_created_at(columns, transaction)
                self.verify_description(columns, transaction)

    def verify_amount(self, columns, transaction):
        element = columns[0]
        self.verify_amount_value(element, transaction)
        self.verify_amount_icon_classes(element, transaction)
        self.verify_amount_link_href(element, transaction)
        self.verify_amount_link_classes(element, transaction)

    def verify_amount_value(self, element, transaction):
        amount = element.text
        localized_amount = formats.localize(transaction.amount, use_l10n=True)
        expected_amount = f"{localized_amount} {transaction.currency.representation}"

        self.assertEqual(amount, expected_amount)

    def verify_amount_icon_classes(self, parent, transaction):
        icon = parent.find_element_by_tag_name("i")

        classes = icon.get_attribute("class")
        expected_classes = transaction.type_icon_class

        self.assertEqual(classes, expected_classes)

    def verify_amount_link_href(self, parent, transaction):
        link = parent.find_element_by_tag_name("a")

        href = link.get_attribute("href")
        expected_href = f"{self.live_server_url}{transaction.get_absolute_url()}"

        self.assertEqual(href, expected_href)

    def verify_amount_link_classes(self, parent, transaction):
        link = parent.find_element_by_tag_name("a")

        classes = link.get_attribute("class").strip()
        expected_classes = "text-success" if transaction.is_income else "text-danger"

        self.assertEqual(classes, expected_classes)

    def verify_account(self, columns, transaction):
        account = columns[1].text
        expected_account = transaction.account.name

        self.assertEqual(account, expected_account)

    def verify_category(self, columns, transaction):
        category = columns[2].text
        expected_category = transaction.category.name

        self.assertEqual(category, expected_category)

    def verify_tags(self, columns, transaction):
        transaction_tags = transaction.tags.all()

        for index, element in enumerate(columns[3].find_elements_by_tag_name("span")):
            with self.subTest(tag_name=element.text):
                self.assertEqual(element.text, transaction_tags[index].name)

    def verify_created_at(self, columns, transaction):
        created_at = columns[4].text
        expected_created_at = formats.date_format(
            transaction.created_at.astimezone(), "SHORT_DATETIME_FORMAT"
        )

        self.assertEqual(created_at, expected_created_at)

    def verify_description(self, columns, transaction):
        description = columns[5].text
        expected_description = transaction.description

        self.assertEqual(description, expected_description)
