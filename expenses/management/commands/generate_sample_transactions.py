from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from expenses.models import Category, Transaction


User = get_user_model()

SAMPLE_NOTE = "[GENERATED SAMPLE DATA]"


SAMPLE_MONTH = [
    {
        "type": Transaction.INCOME,
        "description": "Monthly Paycheck",
        "amount": Decimal("1850.00"),
        "category": None,
        "day": 3,
    },
    {
        "type": Transaction.INCOME,
        "description": "Part-Time Work",
        "amount": Decimal("425.00"),
        "category": None,
        "day": 17,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Rent",
        "amount": Decimal("1200.00"),
        "category": "Housing",
        "day": 1,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Groceries",
        "amount": Decimal("92.40"),
        "category": "Food",
        "day": 5,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Gas",
        "amount": Decimal("48.75"),
        "category": "Transportation",
        "day": 8,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Electric Bill",
        "amount": Decimal("71.35"),
        "category": "Utilities",
        "day": 10,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Lunch",
        "amount": Decimal("18.25"),
        "category": "Food",
        "day": 12,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Streaming Services",
        "amount": Decimal("24.98"),
        "category": "Subscriptions",
        "day": 14,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Household Supplies",
        "amount": Decimal("36.50"),
        "category": "Shopping",
        "day": 16,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Dinner With Friends",
        "amount": Decimal("42.60"),
        "category": "Food",
        "day": 19,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Movie Night",
        "amount": Decimal("28.00"),
        "category": "Entertainment",
        "day": 21,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "School Supplies",
        "amount": Decimal("54.25"),
        "category": "Education",
        "day": 23,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Groceries",
        "amount": Decimal("78.15"),
        "category": "Food",
        "day": 25,
    },
    {
        "type": Transaction.EXPENSE,
        "description": "Gas",
        "amount": Decimal("51.20"),
        "category": "Transportation",
        "day": 27,
    },
]


class Command(BaseCommand):
    help = (
        "Generates several months of deterministic sample "
        "transactions for an Expense Tracker user."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            nargs="?",
            default="demo",
            help="User to generate data for. Default: demo",
        )

        parser.add_argument(
            "--months",
            type=int,
            default=6,
            help="Number of months to generate. Default: 6",
        )

        parser.add_argument(
            "--reset",
            action="store_true",
            help=(
                "Delete previously generated sample transactions "
                "for this user before generating new ones."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        months = options["months"]
        reset = options["reset"]

        if months < 1:
            raise CommandError(
                "--months must be at least 1."
            )

        if months > 24:
            raise CommandError(
                "--months cannot be greater than 24."
            )

        try:
            user = User.objects.get(
                username=username
            )
        except User.DoesNotExist:
            raise CommandError(
                f'User "{username}" does not exist. '
                f'Run "python manage.py seed_demo_data" first '
                f'or provide another username.'
            )

        if reset:
            deleted_count, _ = (
                Transaction.objects
                .filter(
                    user=user,
                    notes__contains=SAMPLE_NOTE,
                )
                .delete()
            )

            self.stdout.write(
                self.style.WARNING(
                    f"Removed {deleted_count} previously "
                    f"generated sample transaction(s)."
                )
            )

        categories = self.get_categories(user)

        today = timezone.localdate()
        current_month = today.replace(day=1)

        created_count = 0
        existing_count = 0

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Generating {months} months of sample data "
                f'for "{username}"'
            )
        )

        self.stdout.write("")

        # Start with the month before the current month.
        # Current month is already handled by seed_demo_data.
        for offset in range(months, 0, -1):
            month_date = self.shift_month(
                current_month,
                -offset,
            )

            created, existing = self.generate_month(
                user=user,
                categories=categories,
                month_date=month_date,
                offset=offset,
            )

            created_count += created
            existing_count += existing

            self.stdout.write(
                f"{month_date.strftime('%B %Y')}: "
                f"{created} created, "
                f"{existing} already existed"
            )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Sample transaction generation complete."
            )
        )

        self.stdout.write(
            f"Created: {created_count}"
        )

        self.stdout.write(
            f"Already existed: {existing_count}"
        )

        self.stdout.write(
            f"Total transactions for {username}: "
            f"{Transaction.objects.filter(user=user).count()}"
        )

    def get_categories(self, user):
        required_categories = [
            "Food",
            "Housing",
            "Transportation",
            "Utilities",
            "Shopping",
            "Entertainment",
            "Subscriptions",
            "Education",
        ]

        categories = {}

        for name in required_categories:
            category, _ = Category.objects.get_or_create(
                user=user,
                name=name,
            )

            categories[name] = category

        return categories

    def shift_month(self, month_date, offset):
        """
        Shift a first-of-month date forward/backward by
        the requested number of months.
        """
        month_index = (
            month_date.year * 12
            + month_date.month
            - 1
            + offset
        )

        year = month_index // 12
        month = month_index % 12 + 1

        return date(
            year,
            month,
            1,
        )

    def generate_month(
        self,
        user,
        categories,
        month_date,
        offset,
    ):
        created_count = 0
        existing_count = 0

        last_day = monthrange(
            month_date.year,
            month_date.month,
        )[1]

        for index, item in enumerate(SAMPLE_MONTH):
            transaction_day = min(
                item["day"],
                last_day,
            )

            transaction_date = date(
                month_date.year,
                month_date.month,
                transaction_day,
            )

            category = None

            if item["category"]:
                category = categories[
                    item["category"]
                ]

            # Slight deterministic variation between months.
            # This makes reports more realistic without random
            # data changing every time the command is run.
            variation = Decimal(
                str(((offset + index) % 5) * 2)
            )

            amount = item["amount"]

            if item["type"] == Transaction.EXPENSE:
                amount += variation

            notes = (
                f"{SAMPLE_NOTE} "
                f"{month_date.strftime('%Y-%m')}"
            )

            _, created = (
                Transaction.objects.get_or_create(
                    user=user,
                    transaction_type=item["type"],
                    description=item["description"],
                    amount=amount,
                    category=category,
                    date=transaction_date,
                    notes=notes,
                )
            )

            if created:
                created_count += 1
            else:
                existing_count += 1

        return created_count, existing_count