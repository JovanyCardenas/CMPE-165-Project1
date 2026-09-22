from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from expenses.models import Budget, Category, Transaction


User = get_user_model()


class CategoryViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpassword123",
        )

        self.category = Category.objects.create(
            user=self.user,
            name="Food",
        )

        self.other_category = Category.objects.create(
            user=self.other_user,
            name="Private Category",
        )

    def login(self):
        self.client.login(
            username="testuser",
            password="testpassword123",
        )

    def test_category_list_requires_login(self):
        response = self.client.get(
            reverse("expenses:category_list")
        )

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_view_category_list(self):
        self.login()

        response = self.client.get(
            reverse("expenses:category_list")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Food",
        )

    def test_user_only_sees_own_categories(self):
        self.login()

        response = self.client.get(
            reverse("expenses:category_list")
        )

        self.assertContains(
            response,
            "Food",
        )

        self.assertNotContains(
            response,
            "Private Category",
        )

    def test_user_can_create_category(self):
        self.login()

        response = self.client.post(
            reverse("expenses:category_create"),
            {
                "name": "Travel",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Category.objects.filter(
                user=self.user,
                name="Travel",
            ).exists()
        )

    def test_duplicate_category_is_rejected(self):
        self.login()

        response = self.client.post(
            reverse("expenses:category_create"),
            {
                "name": "Food",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Category.objects.filter(
                user=self.user,
                name="Food",
            ).count(),
            1,
        )

        self.assertContains(
            response,
            "You already have a category with this name.",
        )

    def test_duplicate_category_is_case_insensitive(self):
        self.login()

        response = self.client.post(
            reverse("expenses:category_create"),
            {
                "name": "food",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Category.objects.filter(
                user=self.user,
                name__iexact="food",
            ).count(),
            1,
        )

    def test_user_can_edit_own_category(self):
        self.login()

        response = self.client.post(
            reverse(
                "expenses:category_update",
                args=[self.category.pk],
            ),
            {
                "name": "Groceries",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.category.refresh_from_db()

        self.assertEqual(
            self.category.name,
            "Groceries",
        )

    def test_user_cannot_edit_other_users_category(self):
        self.login()

        response = self.client.get(
            reverse(
                "expenses:category_update",
                args=[self.other_category.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_other_users_category(self):
        self.login()

        response = self.client.post(
            reverse(
                "expenses:category_delete",
                args=[self.other_category.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Category.objects.filter(
                pk=self.other_category.pk
            ).exists()
        )

    def test_user_can_delete_unused_category(self):
        category = Category.objects.create(
            user=self.user,
            name="Unused",
        )

        self.login()

        response = self.client.post(
            reverse(
                "expenses:category_delete",
                args=[category.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Category.objects.filter(
                pk=category.pk
            ).exists()
        )

    def test_deleting_category_does_not_delete_transactions(self):
        transaction = Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Dinner",
            amount=Decimal("30.00"),
            category=self.category,
            date=date(2026, 9, 20),
        )

        self.login()

        response = self.client.post(
            reverse(
                "expenses:category_delete",
                args=[self.category.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Category.objects.filter(
                pk=self.category.pk
            ).exists()
        )

        self.assertTrue(
            Transaction.objects.filter(
                pk=transaction.pk
            ).exists()
        )

        transaction.refresh_from_db()

        self.assertIsNone(transaction.category)

    def test_category_with_budget_cannot_be_deleted(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("300.00"),
            month=date(2026, 9, 1),
        )

        self.login()

        response = self.client.post(
            reverse(
                "expenses:category_delete",
                args=[self.category.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Category.objects.filter(
                pk=self.category.pk
            ).exists()
        )

        self.assertTrue(
            Budget.objects.filter(
                category=self.category,
            ).exists()
        )

    def test_category_list_displays_transaction_count(self):
        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Lunch",
            amount=Decimal("15.00"),
            category=self.category,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Dinner",
            amount=Decimal("25.00"),
            category=self.category,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:category_list")
        )

        self.assertEqual(response.status_code, 200)

        category = response.context["categories"].get(
            pk=self.category.pk
        )

        self.assertEqual(
            category.transaction_count,
            2,
        )