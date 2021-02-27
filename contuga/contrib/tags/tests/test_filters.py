from django.test import RequestFactory, TestCase
from django.urls import reverse

from contuga.contrib.tags.filters import TagFilterSet
from contuga.mixins import TestMixin


class TagFilterTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()

        self.first_tag = self.create_tag(name="Tag 1")
        self.second_tag = self.create_tag(name="Tag 2")
        self.third_tag = self.create_tag(name="Third tag")

        request_factory = RequestFactory()
        url = reverse("tags:list")
        self.request = request_factory.get(url)
        self.request.user = self.user

    def test_starts_with_filter(self):
        data = {"name__startswith": "Tag"}
        filter = TagFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.first_tag, self.second_tag])

        data = {"name__startswith": "Third"}
        filter = TagFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.third_tag])
