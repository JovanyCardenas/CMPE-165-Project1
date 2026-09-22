from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from expenses.models import Budget, Category, Transaction


User = get_user_model()


class CategoryModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

    def test_category_can_be_created(self):
        category = Category.objects.create(
            user=self.user,
            name="Food",
        )

        self.assertEqual(category.name, "Food")
        self.assertEqual(category.user, self.user)
        self.assertEqual(str(category), "Food")

    def test_same_user_cannot_have_duplicate_category(self):
        Category.objects.create(
            user=self.user,
            name="Food",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(
                    user=self.user,
                    name="Food",
                )

    def test_different_users_can_have_same_category_name(self):
        second_user = User.objects.create_user(
            username="seconduser",
            password="testpassword123",
        )

        Category.objects.create(
            user=self.user,
            name="Food",
        )

        second_category = Category.objects.create(
            user=second_user,
            name="Food",
        )

        self.assertEqual(second_category.name, "Food")
        self.assertEqual(second_category.user, second_user)


class TransactionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.category = Category.objects.create(
            user=self.user,
            name="Food",
        )

    def test_expense_can_be_created(self):
        expense = Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Groceries",
            amount=Decimal("75.50"),
            category=self.category,
            date=date(2026, 9, 20),
        )

        self.assertEqual(expense.user, self.user)
        self.assertEqual(expense.transaction_type, Transaction.EXPENSE)
        self.assertEqual(expense.description, "Groceries")
        self.assertEqual(expense.amount, Decimal("75.50"))
        self.assertEqual(expense.category, self.category)

    def test_income_can_be_created(self):
        income = Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.INCOME,
            description="Paycheck",
            amount=Decimal("1200.00"),
            date=date(2026, 9, 20),
        )

        self.assertEqual(income.transaction_type, Transaction.INCOME)
        self.assertEqual(income.amount, Decimal("1200.00"))

    def test_category_becomes_null_when_category_deleted(self):
        expense = Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Lunch",
            amount=Decimal("15.00"),
            category=self.category,
        )

        self.category.delete()

        expense.refresh_from_db()

        self.assertIsNone(expense.category)

    def test_transaction_string_representation(self):
        expense = Transaction.objects.create(
            user=self.user,
            description="Coffee",
            amount=Decimal("5.25"),
            category=self.category,
        )

        self.assertEqual(
            str(expense),
            "Coffee - $5.25",
        )


class BudgetModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.category = Category.objects.create(
            user=self.user,
            name="Food",
        )

    def test_budget_can_be_created(self):
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("400.00"),
            month=date(2026, 9, 1),
        )

        self.assertEqual(budget.user, self.user)
        self.assertEqual(budget.category, self.category)
        self.assertEqual(budget.amount, Decimal("400.00"))
        self.assertEqual(budget.month, date(2026, 9, 1))

    def test_duplicate_monthly_category_budget_not_allowed(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("400.00"),
            month=date(2026, 9, 1),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Budget.objects.create(
                    user=self.user,
                    category=self.category,
                    amount=Decimal("500.00"),
                    month=date(2026, 9, 1),
                )

    def test_same_category_can_have_budget_for_different_month(self):
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("400.00"),
            month=date(2026, 9, 1),
        )

        october_budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("450.00"),
            month=date(2026, 10, 1),
        )

        self.assertEqual(
            october_budget.month,
            date(2026, 10, 1),
        )

    def test_budget_deleted_when_category_deleted(self):
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("400.00"),
            month=date(2026, 9, 1),
        )

        budget_id = budget.id

        self.category.delete()

        self.assertFalse(
            Budget.objects.filter(id=budget_id).exists()
        )