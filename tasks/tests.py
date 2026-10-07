from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Priority, Task


class LookupCrudTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="student", password="secret")
        self.client.force_login(self.user)

    def test_category_crud(self):
        create_url = reverse("category_create")
        response = self.client.post(create_url, {"name": "Research"})
        self.assertRedirects(response, reverse("category_list"))
        category = Category.objects.get(name="Research")

        update_url = reverse("category_update", args=[category.pk])
        response = self.client.post(update_url, {"name": "Library research"})
        self.assertRedirects(response, reverse("category_list"))
        category.refresh_from_db()
        self.assertEqual(category.name, "Library research")

        delete_url = reverse("category_delete", args=[category.pk])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("category_list"))
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_priority_crud(self):
        create_url = reverse("priority_create")
        response = self.client.post(create_url, {"name": "High"})
        self.assertRedirects(response, reverse("priority_list"))
        priority = Priority.objects.get(name="High")

        update_url = reverse("priority_update", args=[priority.pk])
        response = self.client.post(update_url, {"name": "Critical"})
        self.assertRedirects(response, reverse("priority_list"))
        priority.refresh_from_db()
        self.assertEqual(priority.name, "Critical")

        delete_url = reverse("priority_delete", args=[priority.pk])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("priority_list"))
        self.assertFalse(Priority.objects.filter(pk=priority.pk).exists())

    def test_associated_lookup_cannot_be_deleted(self):
        category = Category.objects.create(name="Work")
        priority = Priority.objects.create(name="High")
        Task.objects.create(
            title="Submit report",
            description="Finish the report",
            deadline="2030-01-01T09:00:00Z",
            category=category,
            priority=priority,
            user=self.user,
        )

        response = self.client.post(reverse("category_delete", args=[category.pk]))
        self.assertRedirects(response, reverse("category_list"))
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())

    def test_sidebar_links_are_available(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, reverse("category_list"))
        self.assertContains(response, reverse("priority_list"))

    def test_lookup_routes_require_login(self):
        self.client.logout()

        category_response = self.client.get(reverse("category_list"))
        self.assertEqual(category_response.status_code, 302)
        self.assertEqual(category_response.url, reverse("login") + "?next=/categories/")

        priority_response = self.client.get(reverse("priority_list"))
        self.assertEqual(priority_response.status_code, 302)
        self.assertEqual(priority_response.url, reverse("login") + "?next=/priorities/")
