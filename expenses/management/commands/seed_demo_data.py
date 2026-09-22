from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from expenses.models import Budget, Category, Transaction


User = get_user_model()


DEMO_USERNAME = "demo"
DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "Demo12345!"

DEMO_NOTE = "[DEMO DATA]"


class Command(BaseCommand):
    help = "Creates a demo user with realistic Expense Tracker data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo financial data before reseeding.",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Expense Tracker Demo Data"
            )
        )

        user, created = User.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={
                "email": DEMO_EMAIL,
                "first_name": "Demo",
                "last_name": "User",
            },
        )

        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    "Created demo user."
                )
            )
        else:
            self.stdout.write(
                "Demo user already exists."
            )

        if options["reset"]:
            self.clear_demo_financial_data(user)

        categories = self.create_categories(user)

        today = timezone.localdate()
        current_month = today.replace(day=1)

        self.create_budgets(
            user,
            categories,
            current_month,
        )

        self.create_current_month_transactions(
            user,
            categories,
            today,
        )

        self.create_previous_month_transactions(
            user,
            categories,
            current_month,
        )

        self.print_summary(user)

    def clear_demo_financial_data(self, user):
        demo_transactions = Transaction.objects.filter(
            user=user,
            notes__contains=DEMO_NOTE,
        )

        transaction_count = demo_transactions.count()

        demo_transactions.delete()

        # The demo account exists specifically for generated demo data,
        # so its budgets can safely be regenerated.
        budget_count = Budget.objects.filter(
            user=user
        ).count()

        Budget.objects.filter(
            user=user
        ).delete()

        self.stdout.write(
            self.style.WARNING(
                f"Reset {transaction_count} demo transactions "
                f"and {budget_count} demo budgets."
            )
        )

    def create_categories(self, user):
        category_names = [
            "Food",
            "Housing",
            "Transportation",
            "Utilities",
            "Shopping",
            "Entertainment",
            "Subscriptions",
            "Health",
            "Education",
            "Other",
        ]

        categories = {}

        for name in category_names:
            category, created = Category.objects.get_or_create(
                user=user,
                name=name,
            )

            categories[name] = category

            if created:
                self.stdout.write(
                    f"Created category: {name}"
                )

        return categories

    def create_budgets(
        self,
        user,
        categories,
        current_month,
    ):
        budgets = [
            ("Food", "450.00"),
            ("Housing", "1200.00"),
            ("Transportation", "250.00"),
            ("Utilities", "180.00"),
            ("Shopping", "150.00"),
            ("Entertainment", "120.00"),
            ("Subscriptions", "75.00"),
        ]

        created_count = 0

        for category_name, amount in budgets:
            _, created = Budget.objects.get_or_create(
                user=user,
                category=categories[category_name],
                month=current_month,
                defaults={
                    "amount": Decimal(amount),
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} monthly budgets."
            )
        )

    def create_current_month_transactions(
        self,
        user,
        categories,
        today,
    ):
        transactions = [
            {
                "type": Transaction.INCOME,
                "description": "Paycheck",
                "amount": "1450.00",
                "category": None,
                "days_ago": 2,
            },
            {
                "type": Transaction.INCOME,
                "description": "Freelance Project",
                "amount": "325.00",
                "category": None,
                "days_ago": 5,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Rent",
                "amount": "1200.00",
                "category": "Housing",
                "days_ago": 1,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Weekly Groceries",
                "amount": "86.42",
                "category": "Food",
                "days_ago": 3,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Gas",
                "amount": "52.18",
                "category": "Transportation",
                "days_ago": 4,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Electric Bill",
                "amount": "74.63",
                "category": "Utilities",
                "days_ago": 6,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Dinner With Friends",
                "amount": "38.75",
                "category": "Food",
                "days_ago": 7,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Streaming Services",
                "amount": "24.98",
                "category": "Subscriptions",
                "days_ago": 8,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Movie Night",
                "amount": "22.50",
                "category": "Entertainment",
                "days_ago": 9,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "School Supplies",
                "amount": "47.29",
                "category": "Education",
                "days_ago": 10,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Coffee",
                "amount": "6.45",
                "category": "Food",
                "days_ago": 11,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Household Supplies",
                "amount": "31.84",
                "category": "Shopping",
                "days_ago": 12,
            },
        ]

        created_count = 0

        month_start = today.replace(day=1)

        for item in transactions:
            transaction_date = today - timedelta(
                days=item["days_ago"]
            )

            # Keep current-month demo transactions in the
            # current month even when run near the beginning.
            if transaction_date < month_start:
                transaction_date = month_start

            category = None

            if item["category"]:
                category = categories[item["category"]]

            _, created = Transaction.objects.get_or_create(
                user=user,
                description=item["description"],
                amount=Decimal(item["amount"]),
                date=transaction_date,
                notes=DEMO_NOTE,
                defaults={
                    "transaction_type": item["type"],
                    "category": category,
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} current-month transactions."
            )
        )

    def create_previous_month_transactions(
        self,
        user,
        categories,
        current_month,
    ):
        previous_month_last_day = (
            current_month - timedelta(days=1)
        )

        previous_month = (
            previous_month_last_day.replace(day=1)
        )

        transactions = [
            {
                "type": Transaction.INCOME,
                "description": "Previous Month Paycheck",
                "amount": "1500.00",
                "category": None,
                "day": 5,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Previous Month Rent",
                "amount": "1200.00",
                "category": "Housing",
                "day": 6,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Previous Month Groceries",
                "amount": "164.35",
                "category": "Food",
                "day": 12,
            },
            {
                "type": Transaction.EXPENSE,
                "description": "Previous Month Gas",
                "amount": "61.40",
                "category": "Transportation",
                "day": 18,
            },
        ]

        created_count = 0

        for item in transactions:
            transaction_date = date(
                previous_month.year,
                previous_month.month,
                item["day"],
            )

            category = None

            if item["category"]:
                category = categories[item["category"]]

            _, created = Transaction.objects.get_or_create(
                user=user,
                description=item["description"],
                amount=Decimal(item["amount"]),
                date=transaction_date,
                notes=DEMO_NOTE,
                defaults={
                    "transaction_type": item["type"],
                    "category": category,
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} previous-month transactions."
            )
        )

    def print_summary(self, user):
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Demo data is ready."
            )
        )

        self.stdout.write("")
        self.stdout.write(
            f"Username: {DEMO_USERNAME}"
        )
        self.stdout.write(
            f"Password: {DEMO_PASSWORD}"
        )

        self.stdout.write("")
        self.stdout.write(
            f"Categories: "
            f"{Category.objects.filter(user=user).count()}"
        )

        self.stdout.write(
            f"Transactions: "
            f"{Transaction.objects.filter(user=user).count()}"
        )

        self.stdout.write(
            f"Budgets: "
            f"{Budget.objects.filter(user=user).count()}"
        )

        self.stdout.write("")
        self.stdout.write(
            "Open the application and log in with the demo account."
        )