from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail, signing
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from contuga.mixins import TestMixin

UserModel = get_user_model()


class UsersTestCase(TestCase, TestMixin):
    def test_registration_get(self):
        url = reverse("users:registration")
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_registration(self):
        data = {
            "email": "john.doe@example.com",
            "password1": "Secret123+",
            "password2": "Secret123+",
        }
        old_user_count = UserModel.objects.count()

        self.assertEqual(len(mail.outbox), 0)

        url = reverse("users:registration")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert new user is created
        new_user_count = UserModel.objects.count()
        self.assertEqual(new_user_count, old_user_count + 1)

        # Assert user is saved correctly
        user = UserModel.objects.order_by("date_joined").last()
        self.assertEqual(user.email, data["email"])

        # Assert success message is showed
        success_text = _(
            "Your registration is successful. An activation link has been sent to your email."
        )
        self.assertContains(response=response, text=success_text)

        self.assertEqual(len(mail.outbox), 1)

        activation_key = self.get_activation_key(user)
        activation_link = self.get_activation_link(
            activation_key, response.wsgi_request
        )
        message = mail.outbox[0]

        self.assertIn(activation_link, message.body)

    def test_activation(self):
        user = self.create_user(is_active=False)
        activation_key = self.get_activation_key(user)
        url = reverse("users:activate", args=[activation_key])

        self.assertFalse(user.is_active)

        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)

        activated_user = UserModel.objects.get(pk=user.pk)
        self.assertTrue(activated_user.is_active)

        success_text = _("Your activation was successful")
        self.assertContains(response=response, text=success_text)

    def test_login(self):
        data = {"username": "john.doe@example.com", "password": "Secret123+"}

        self.create_user(email=data["username"], password=data["password"])

        url = reverse("users:login")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert user is authenticated
        user = response.context["user"]
        self.assertTrue(user.is_authenticated)

        self.assertAlmostEqual(
            user.last_login, timezone.now(), delta=timezone.timedelta(seconds=1)
        )

        # Assert user is redirected to the transaction view
        self.assertRedirects(
            response,
            reverse("transactions:list"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def get_activation_key(self, user):
        REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")
        return signing.dumps(obj=user.get_username(), salt=REGISTRATION_SALT)

    def get_activation_link(self, activation_key, wsgi_request):
        return wsgi_request.build_absolute_uri(
            reverse("users:activate", args=[activation_key])
        )
