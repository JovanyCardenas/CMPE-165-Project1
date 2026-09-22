from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from expenses.models import Category, Transaction


User = get_user_model()


class TransactionViewTests(TestCase):

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
            name="Food",
        )

    def test_transaction_list_requires_login(self):
        response = self.client.get(
            reverse("expenses:transaction_list")
        )

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_view_transaction_list(self):
        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(
            reverse("expenses:transaction_list")
        )

        self.assertEqual(response.status_code, 200)

    def test_user_can_create_expense(self):
        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.post(
            reverse("expenses:transaction_create"),
            {
                "transaction_type": Transaction.EXPENSE,
                "description": "Groceries",
                "amount": "85.25",
                "category": self.category.id,
                "date": "2026-09-20",
                "notes": "Weekly groceries",
            },
        )

        self.assertEqual(response.status_code, 302)

        expense = Transaction.objects.get(
            user=self.user,
            description="Groceries",
        )

        self.assertEqual(
            expense.amount,
            Decimal("85.25"),
        )

        self.assertEqual(
            expense.transaction_type,
            Transaction.EXPENSE,
        )

    def test_user_can_create_income(self):
        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.post(
            reverse("expenses:transaction_create"),
            {
                "transaction_type": Transaction.INCOME,
                "description": "Paycheck",
                "amount": "1250.00",
                "category": "",
                "date": "2026-09-20",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Transaction.objects.filter(
                user=self.user,
                description="Paycheck",
                transaction_type=Transaction.INCOME,
            ).exists()
        )

    def test_user_can_edit_own_transaction(self):
        expense = Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Lunch",
            amount=Decimal("15.00"),
            category=self.category,
            date=date(2026, 9, 20),
        )

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.post(
            reverse(
                "expenses:transaction_update",
                args=[expense.pk],
            ),
            {
                "transaction_type": Transaction.EXPENSE,
                "description": "Dinner",
                "amount": "25.00",
                "category": self.category.id,
                "date": "2026-09-20",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 302)

        expense.refresh_from_db()

        self.assertEqual(
            expense.description,
            "Dinner",
        )

        self.assertEqual(
            expense.amount,
            Decimal("25.00"),
        )

    def test_user_can_delete_own_transaction(self):
        expense = Transaction.objects.create(
            user=self.user,
            description="Coffee",
            amount=Decimal("5.00"),
            category=self.category,
        )

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.post(
            reverse(
                "expenses:transaction_delete",
                args=[expense.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Transaction.objects.filter(
                pk=expense.pk
            ).exists()
        )

    def test_user_cannot_view_other_users_transaction_on_list(self):
        Transaction.objects.create(
            user=self.other_user,
            description="Private Expense",
            amount=Decimal("999.00"),
            category=self.other_category,
        )

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(
            reverse("expenses:transaction_list")
        )

        self.assertNotContains(
            response,
            "Private Expense",
        )

    def test_user_cannot_edit_other_users_transaction(self):
        transaction = Transaction.objects.create(
            user=self.other_user,
            description="Other User Expense",
            amount=Decimal("100.00"),
            category=self.other_category,
        )

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(
            reverse(
                "expenses:transaction_update",
                args=[transaction.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_user_cannot_delete_other_users_transaction(self):
        transaction = Transaction.objects.create(
            user=self.other_user,
            description="Other User Expense",
            amount=Decimal("100.00"),
            category=self.other_category,
        )

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.post(
            reverse(
                "expenses:transaction_delete",
                args=[transaction.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertTrue(
            Transaction.objects.filter(
                pk=transaction.pk
            ).exists()
        )