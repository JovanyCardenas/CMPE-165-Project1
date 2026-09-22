from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from expenses.models import Budget, Category, Transaction


User = get_user_model()


class BudgetViewTests(TestCase):

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

        self.transportation_category = Category.objects.create(
            user=self.user,
            name="Transportation",
        )

        self.other_category = Category.objects.create(
            user=self.other_user,
            name="Food",
        )

    def login(self):
        self.client.login(
            username="testuser",
            password="testpassword123",
        )

    def test_budget_list_requires_login(self):
        response = self.client.get(
            reverse("expenses:budget_list")
        )

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_view_budget_list(self):
        self.login()

        response = self.client.get(
            reverse("expenses:budget_list")
        )

        self.assertEqual(response.status_code, 200)

    def test_user_can_create_budget(self):
        self.login()

        response = self.client.post(
            reverse("expenses:budget_create"),
            {
                "category": self.category.pk,
                "amount": "400.00",
                "month": "2026-09",
            },
        )

        self.assertEqual(response.status_code, 302)

        budget = Budget.objects.get(
            user=self.user,
            category=self.category,
        )

        self.assertEqual(
            budget.amount,
            Decimal("400.00"),
        )

        self.assertEqual(
            budget.month,
            date(2026, 9, 1),
        )

    def test_budget_month_is_saved_as_first_day_of_month(self):
        self.login()

        response = self.client.post(
            reverse("expenses:budget_create"),
            {
                "category": self.category.pk,
                "amount": "350.00",
                "month": "2026-10",
            },
        )

        self.assertEqual(response.status_code, 302)

        budget = Budget.objects.get(
            user=self.user,
            category=self.category,
        )

        self.assertEqual(
            budget.month,
            date(2026, 10, 1),
        )

    def test_user_can_edit_own_budget(self):
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("300.00"),
            month=date(2026, 9, 1),
        )

        self.login()

        response = self.client.post(
            reverse(
                "expenses:budget_update",
                args=[budget.pk],
            ),
            {
                "category": self.category.pk,
                "amount": "450.00",
                "month": "2026-09",
            },
        )

        self.assertEqual(response.status_code, 302)

        budget.refresh_from_db()

        self.assertEqual(
            budget.amount,
            Decimal("450.00"),
        )

    def test_user_can_delete_own_budget(self):
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("300.00"),
            month=date(2026, 9, 1),
        )

        self.login()

        response = self.client.post(
            reverse(
                "expenses:budget_delete",
                args=[budget.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Budget.objects.filter(
                pk=budget.pk
            ).exists()
        )

    def test_user_only_sees_own_budgets(self):
        own_budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("300.00"),
            month=date(2026, 9, 1),
        )

        Budget.objects.create(
            user=self.other_user,
            category=self.other_category,
            amount=Decimal("9999.00"),
            month=date(2026, 9, 1),
        )

        self.login()

        response = self.client.get(
            reverse("expenses:budget_list")
        )

        self.assertEqual(response.status_code, 200)

        budget_data = response.context["budget_data"]

        self.assertEqual(
            len(budget_data),
            1,
        )

        self.assertEqual(
            budget_data[0]["budget"].pk,
            own_budget.pk,
        )

        self.assertEqual(
            budget_data[0]["budget"].user,
            self.user,
        )

    def test_user_cannot_edit_other_users_budget(self):
        budget = Budget.objects.create(
            user=self.other_user,
            category=self.other_category,
            amount=Decimal("500.00"),
            month=date(2026, 9, 1),
        )

        self.login()

        response = self.client.get(
            reverse(
                "expenses:budget_update",
                args=[budget.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_other_users_budget(self):
        budget = Budget.objects.create(
            user=self.other_user,
            category=self.other_category,
            amount=Decimal("500.00"),
            month=date(2026, 9, 1),
        )

        self.login()

        response = self.client.post(
            reverse(
                "expenses:budget_delete",
                args=[budget.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Budget.objects.filter(
                pk=budget.pk
            ).exists()
        )

    def test_user_cannot_create_budget_with_other_users_category(self):
        self.login()

        response = self.client.post(
            reverse("expenses:budget_create"),
            {
                "category": self.other_category.pk,
                "amount": "500.00",
                "month": "2026-09",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Budget.objects.filter(
                user=self.user,
                category=self.other_category,
            ).exists()
        )

    def test_duplicate_budget_for_same_category_and_month_is_rejected(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("300.00"),
            month=date(2026, 9, 1),
        )

        self.login()

        response = self.client.post(
            reverse("expenses:budget_create"),
            {
                "category": self.category.pk,
                "amount": "500.00",
                "month": "2026-09",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Budget.objects.filter(
                user=self.user,
                category=self.category,
                month=date(2026, 9, 1),
            ).count(),
            1,
        )

        self.assertContains(
            response,
            "You already have a budget for this category and month.",
        )

    def test_same_category_can_have_budget_in_different_month(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("300.00"),
            month=date(2026, 9, 1),
        )

        self.login()

        response = self.client.post(
            reverse("expenses:budget_create"),
            {
                "category": self.category.pk,
                "amount": "400.00",
                "month": "2026-10",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Budget.objects.filter(
                user=self.user,
                category=self.category,
            ).count(),
            2,
        )

    def test_editing_budget_into_duplicate_is_rejected(self):
        first_budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("300.00"),
            month=date(2026, 9, 1),
        )

        second_budget = Budget.objects.create(
            user=self.user,
            category=self.transportation_category,
            amount=Decimal("200.00"),
            month=date(2026, 9, 1),
        )

        self.login()

        response = self.client.post(
            reverse(
                "expenses:budget_update",
                args=[second_budget.pk],
            ),
            {
                "category": self.category.pk,
                "amount": "500.00",
                "month": "2026-09",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "You already have a budget for this category and month.",
        )

        second_budget.refresh_from_db()

        self.assertEqual(
            second_budget.category,
            self.transportation_category,
        )

        self.assertEqual(
            Budget.objects.filter(
                user=self.user,
                category=self.category,
                month=date(2026, 9, 1),
            ).count(),
            1,
        )

        self.assertTrue(
            Budget.objects.filter(
                pk=first_budget.pk
            ).exists()
        )


class BudgetCalculationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.category = Category.objects.create(
            user=self.user,
            name="Food",
        )

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

    def get_budget_data_item(self, response):
        """
        Return the budget_data dictionary for this test category.
        """
        budget_data = response.context["budget_data"]

        return next(
            item
            for item in budget_data
            if item["budget"].category_id == self.category.id
        )

    def test_budget_spending_calculation(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("500.00"),
            month=date(2026, 9, 1),
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Groceries",
            amount=Decimal("100.00"),
            category=self.category,
            date=date(2026, 9, 5),
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Restaurant",
            amount=Decimal("50.00"),
            category=self.category,
            date=date(2026, 9, 10),
        )

        response = self.client.get(
            reverse("expenses:budget_list")
        )

        item = self.get_budget_data_item(response)

        self.assertEqual(
            item["spent"],
            Decimal("150.00"),
        )

    def test_budget_remaining_calculation(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("500.00"),
            month=date(2026, 9, 1),
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Groceries",
            amount=Decimal("125.00"),
            category=self.category,
            date=date(2026, 9, 5),
        )

        response = self.client.get(
            reverse("expenses:budget_list")
        )

        item = self.get_budget_data_item(response)

        self.assertEqual(
            item["remaining"],
            Decimal("375.00"),
        )

    def test_budget_percentage_calculation(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("400.00"),
            month=date(2026, 9, 1),
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Groceries",
            amount=Decimal("100.00"),
            category=self.category,
            date=date(2026, 9, 5),
        )

        response = self.client.get(
            reverse("expenses:budget_list")
        )

        item = self.get_budget_data_item(response)

        self.assertEqual(
            item["percentage"],
            Decimal("25.00"),
        )

    def test_income_does_not_count_toward_budget_spending(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("500.00"),
            month=date(2026, 9, 1),
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.INCOME,
            description="Refund",
            amount=Decimal("200.00"),
            category=self.category,
            date=date(2026, 9, 5),
        )

        response = self.client.get(
            reverse("expenses:budget_list")
        )

        item = self.get_budget_data_item(response)

        self.assertEqual(
            item["spent"],
            Decimal("0.00"),
        )

    def test_expense_from_different_month_does_not_count(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("500.00"),
            month=date(2026, 9, 1),
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="August Groceries",
            amount=Decimal("200.00"),
            category=self.category,
            date=date(2026, 8, 20),
        )

        response = self.client.get(
            reverse("expenses:budget_list")
        )

        item = self.get_budget_data_item(response)

        self.assertEqual(
            item["spent"],
            Decimal("0.00"),
        )