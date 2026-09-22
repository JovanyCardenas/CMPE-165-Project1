from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from expenses.models import Budget, Category, Transaction


User = get_user_model()


class DashboardViewTests(TestCase):

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

        self.food = Category.objects.create(
            user=self.user,
            name="Food",
        )

        self.transportation = Category.objects.create(
            user=self.user,
            name="Transportation",
        )

        self.other_category = Category.objects.create(
            user=self.other_user,
            name="Private Category",
        )

        self.today = timezone.localdate()
        self.month_start = self.today.replace(day=1)

    def login(self):
        self.client.login(
            username="testuser",
            password="testpassword123",
        )

    def previous_month_date(self):
        """
        Return a date guaranteed to be in the previous month.
        """
        return self.month_start - timedelta(days=1)

    def test_dashboard_requires_login(self):
        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_view_dashboard(self):
        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(response.status_code, 200)

    def test_empty_dashboard_has_zero_totals(self):
        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["balance"],
            Decimal("0.00"),
        )

        self.assertEqual(
            response.context["total_income"],
            Decimal("0.00"),
        )

        self.assertEqual(
            response.context["total_expenses"],
            Decimal("0.00"),
        )

        self.assertEqual(
            response.context["total_budget"],
            Decimal("0.00"),
        )

        self.assertEqual(
            response.context["budget_remaining"],
            Decimal("0.00"),
        )

    def test_current_month_income_total(self):
        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.INCOME,
            description="Paycheck",
            amount=Decimal("1200.00"),
            date=self.today,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.INCOME,
            description="Side Job",
            amount=Decimal("300.00"),
            date=self.today,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["total_income"],
            Decimal("1500.00"),
        )

    def test_current_month_expense_total(self):
        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Groceries",
            amount=Decimal("100.00"),
            category=self.food,
            date=self.today,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Gas",
            amount=Decimal("50.00"),
            category=self.transportation,
            date=self.today,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["total_expenses"],
            Decimal("150.00"),
        )

    def test_previous_month_transactions_not_in_monthly_totals(self):
        previous_month = self.previous_month_date()

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.INCOME,
            description="Old Income",
            amount=Decimal("500.00"),
            date=previous_month,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Old Expense",
            amount=Decimal("200.00"),
            category=self.food,
            date=previous_month,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["total_income"],
            Decimal("0.00"),
        )

        self.assertEqual(
            response.context["total_expenses"],
            Decimal("0.00"),
        )

    def test_balance_uses_all_time_transactions(self):
        previous_month = self.previous_month_date()

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.INCOME,
            description="Old Income",
            amount=Decimal("1000.00"),
            date=previous_month,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Old Expense",
            amount=Decimal("250.00"),
            category=self.food,
            date=previous_month,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.INCOME,
            description="Current Income",
            amount=Decimal("500.00"),
            date=self.today,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Current Expense",
            amount=Decimal("100.00"),
            category=self.food,
            date=self.today,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        # 1500 total income - 350 total expenses
        self.assertEqual(
            response.context["balance"],
            Decimal("1150.00"),
        )

        # Dashboard cards themselves only represent current month.
        self.assertEqual(
            response.context["total_income"],
            Decimal("500.00"),
        )

        self.assertEqual(
            response.context["total_expenses"],
            Decimal("100.00"),
        )

    def test_current_month_budget_total(self):
        Budget.objects.create(
            user=self.user,
            category=self.food,
            amount=Decimal("400.00"),
            month=self.month_start,
        )

        Budget.objects.create(
            user=self.user,
            category=self.transportation,
            amount=Decimal("200.00"),
            month=self.month_start,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["total_budget"],
            Decimal("600.00"),
        )

    def test_budget_remaining_calculation(self):
        Budget.objects.create(
            user=self.user,
            category=self.food,
            amount=Decimal("500.00"),
            month=self.month_start,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Groceries",
            amount=Decimal("125.00"),
            category=self.food,
            date=self.today,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["budget_remaining"],
            Decimal("375.00"),
        )

    def test_budget_remaining_never_goes_below_zero(self):
        Budget.objects.create(
            user=self.user,
            category=self.food,
            amount=Decimal("100.00"),
            month=self.month_start,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Large Grocery Trip",
            amount=Decimal("175.00"),
            category=self.food,
            date=self.today,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["budget_remaining"],
            Decimal("0.00"),
        )

    def test_budget_percentage_calculation(self):
        Budget.objects.create(
            user=self.user,
            category=self.food,
            amount=Decimal("400.00"),
            month=self.month_start,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Groceries",
            amount=Decimal("100.00"),
            category=self.food,
            date=self.today,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["budget_percentage"],
            Decimal("25.00"),
        )

        self.assertEqual(
            response.context["budget_percentage_display"],
            Decimal("25.00"),
        )

    def test_budget_percentage_display_is_capped_at_100(self):
        Budget.objects.create(
            user=self.user,
            category=self.food,
            amount=Decimal("100.00"),
            month=self.month_start,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Large Expense",
            amount=Decimal("150.00"),
            category=self.food,
            date=self.today,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["budget_percentage"],
            Decimal("150.0"),
        )

        self.assertEqual(
            response.context["budget_percentage_display"],
            Decimal("100"),
        )

    def test_category_spending_calculation(self):
        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Groceries",
            amount=Decimal("75.00"),
            category=self.food,
            date=self.today,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="Gas",
            amount=Decimal("25.00"),
            category=self.transportation,
            date=self.today,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        category_spending = response.context[
            "category_spending"
        ]

        food = next(
            item
            for item in category_spending
            if item["category"] == "Food"
        )

        transportation = next(
            item
            for item in category_spending
            if item["category"] == "Transportation"
        )

        self.assertEqual(
            food["total"],
            Decimal("75.00"),
        )

        self.assertEqual(
            food["percentage"],
            Decimal("75.0"),
        )

        self.assertEqual(
            transportation["total"],
            Decimal("25.00"),
        )

        self.assertEqual(
            transportation["percentage"],
            Decimal("25.0"),
        )

    def test_recent_transactions_limited_to_five(self):
        for number in range(7):
            Transaction.objects.create(
                user=self.user,
                transaction_type=Transaction.EXPENSE,
                description=f"Expense {number}",
                amount=Decimal("10.00"),
                category=self.food,
                date=self.today,
            )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        recent_transactions = list(
            response.context["recent_transactions"]
        )

        self.assertEqual(
            len(recent_transactions),
            5,
        )

    def test_dashboard_does_not_include_other_users_financial_data(self):
        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.INCOME,
            description="My Income",
            amount=Decimal("1000.00"),
            date=self.today,
        )

        Transaction.objects.create(
            user=self.user,
            transaction_type=Transaction.EXPENSE,
            description="My Expense",
            amount=Decimal("100.00"),
            category=self.food,
            date=self.today,
        )

        Transaction.objects.create(
            user=self.other_user,
            transaction_type=Transaction.INCOME,
            description="Other Income",
            amount=Decimal("99999.00"),
            date=self.today,
        )

        Transaction.objects.create(
            user=self.other_user,
            transaction_type=Transaction.EXPENSE,
            description="Other Expense",
            amount=Decimal("88888.00"),
            category=self.other_category,
            date=self.today,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["total_income"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            response.context["total_expenses"],
            Decimal("100.00"),
        )

        self.assertEqual(
            response.context["balance"],
            Decimal("900.00"),
        )

    def test_dashboard_does_not_include_other_users_budgets(self):
        Budget.objects.create(
            user=self.user,
            category=self.food,
            amount=Decimal("500.00"),
            month=self.month_start,
        )

        Budget.objects.create(
            user=self.other_user,
            category=self.other_category,
            amount=Decimal("9999.00"),
            month=self.month_start,
        )

        self.login()

        response = self.client.get(
            reverse("expenses:dashboard")
        )

        self.assertEqual(
            response.context["total_budget"],
            Decimal("500.00"),
        )