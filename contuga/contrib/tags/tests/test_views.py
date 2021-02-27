from django.test import TestCase
from django.urls import reverse

from contuga.mixins import TestMixin

from ..models import Tag


class TagsTestCase(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user(email="john.doe@example.com", password="password")
        self.tag = self.create_tag()
        self.client.force_login(self.user)

    def test_list(self):
        url = reverse("tags:list")
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert queryset is correct
        self.assertQuerysetEqual(
            response.context["tag_list"], Tag.objects.all(), transform=lambda x: x
        )

        # Assert tag name is used
        self.assertContains(response=response, text=self.tag.name)

    def test_detail(self):
        url = reverse("tags:detail", kwargs={"pk": self.tag.pk})
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct model is retrieved
        self.assertEqual(response.context["tag"], self.tag)

        # Assert tag name is used
        self.assertContains(response=response, text=self.tag.name)

    def test_create_get(self):
        url = reverse("tags:create")
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        data = {"name": "New tag name"}
        old_tag_count = Tag.objects.count()

        url = reverse("tags:create")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert new tag is created
        new_tag_count = Tag.objects.count()
        self.assertEqual(new_tag_count, old_tag_count + 1)

        # Assert tag is saved correctly
        tag = Tag.objects.order_by("created_at").last()

        tag_data = {"name": tag.name}
        self.assertDictEqual(tag_data, data)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("tags:detail", kwargs={"pk": tag.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_update_get(self):
        url = reverse("tags:update", kwargs={"pk": self.tag.pk})
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert instance is correct
        instance = response.context.get("object")
        self.assertEqual(instance, self.tag)

        # Assert initial form data is correct
        form = response.context.get("form")
        form_data = {"name": form.initial["name"]}
        expected_data = {"name": self.tag.name}
        self.assertDictEqual(form_data, expected_data)

    def test_update(self):
        data = {"name": "New tag name"}

        url = reverse("tags:update", kwargs={"pk": self.tag.pk})
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("tags:detail", kwargs={"pk": self.tag.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert tag is updated
        tag = Tag.objects.get(pk=self.tag.pk)
        tag_data = {"name": tag.name}
        self.assertDictEqual(tag_data, data)

    def test_delete(self):
        old_tag_count = Tag.objects.count()

        url = reverse("tags:delete", kwargs={"pk": self.tag.pk})
        response = self.client.post(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert tag is deleted
        new_tag_count = Tag.objects.count()
        self.assertEqual(new_tag_count, old_tag_count - 1)
        with self.assertRaises(Tag.DoesNotExist):
            Tag.objects.get(pk=self.tag.pk)
