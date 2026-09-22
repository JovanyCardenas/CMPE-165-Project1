import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from expenses.models import Budget, Category, Transaction


User = get_user_model()


class DecimalEncoder(json.JSONEncoder):
    """
    Allow Decimal values to be written cleanly to JSON.
    """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, date):
            return obj.isoformat()

        return super().default(obj)


class Command(BaseCommand):
    help = (
        "Exports a user's Expense Tracker data "
        "to CSV or JSON files."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            type=str,
            help="Username whose Expense Tracker data will be exported.",
        )

        parser.add_argument(
            "--format",
            choices=["csv", "json"],
            default="csv",
            help="Export format. Default: csv",
        )

        parser.add_argument(
            "--month",
            type=str,
            help=(
                "Optional month filter in YYYY-MM format. "
                "Example: 2026-09"
            ),
        )

        parser.add_argument(
            "--output",
            type=str,
            help=(
                "Optional output directory. "
                "Default: <project>/exports"
            ),
        )

    def handle(self, *args, **options):
        username = options["username"]
        export_format = options["format"]
        selected_month = options.get("month")
        output_option = options.get("output")

        user = self.get_user(username)

        year = None
        month = None

        if selected_month:
            year, month = self.parse_month(
                selected_month
            )

        output_directory = self.get_output_directory(
            username=username,
            output_option=output_option,
            selected_month=selected_month,
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        transactions = (
            Transaction.objects
            .filter(user=user)
            .select_related("category")
            .order_by("-date", "-created_at")
        )

        budgets = (
            Budget.objects
            .filter(user=user)
            .select_related("category")
            .order_by("-month", "category__name")
        )

        categories = (
            Category.objects
            .filter(user=user)
            .order_by("name")
        )

        if selected_month:
            transactions = transactions.filter(
                date__year=year,
                date__month=month,
            )

            budgets = budgets.filter(
                month__year=year,
                month__month=month,
            )

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f'Exporting Expense Tracker data for "{username}"'
            )
        )

        self.stdout.write(
            f"Format: {export_format.upper()}"
        )

        if selected_month:
            self.stdout.write(
                f"Month: {selected_month}"
            )
        else:
            self.stdout.write(
                "Month: All data"
            )

        self.stdout.write("")

        if export_format == "csv":
            files = self.export_csv(
                output_directory=output_directory,
                transactions=transactions,
                budgets=budgets,
                categories=categories,
            )
        else:
            files = self.export_json(
                output_directory=output_directory,
                username=username,
                selected_month=selected_month,
                transactions=transactions,
                budgets=budgets,
                categories=categories,
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Expense data export complete."
            )
        )

        self.stdout.write("")
        self.stdout.write(
            f"Transactions exported: {transactions.count()}"
        )

        self.stdout.write(
            f"Budgets exported: {budgets.count()}"
        )

        self.stdout.write(
            f"Categories exported: {categories.count()}"
        )

        self.stdout.write("")
        self.stdout.write(
            f"Output directory: {output_directory}"
        )

        self.stdout.write("")

        for file_path in files:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created: {file_path.name}"
                )
            )

    def get_user(self, username):
        try:
            return User.objects.get(
                username=username
            )
        except User.DoesNotExist:
            raise CommandError(
                f'User "{username}" does not exist.'
            )

    def parse_month(self, selected_month):
        try:
            year_text, month_text = (
                selected_month.split("-")
            )

            year = int(year_text)
            month = int(month_text)

            # Validate that this is a real year/month.
            date(
                year,
                month,
                1,
            )

        except (ValueError, TypeError):
            raise CommandError(
                'Invalid --month value. '
                'Use YYYY-MM, for example: '
                '"--month 2026-09".'
            )

        return year, month

    def get_output_directory(
        self,
        username,
        output_option,
        selected_month,
    ):
        if output_option:
            base_directory = Path(
                output_option
            ).expanduser()

            if not base_directory.is_absolute():
                base_directory = (
                    Path(settings.BASE_DIR)
                    / base_directory
                )
        else:
            base_directory = (
                Path(settings.BASE_DIR)
                / "exports"
            )

        user_directory = (
            base_directory
            / username
        )

        if selected_month:
            user_directory = (
                user_directory
                / selected_month
            )

        return user_directory

    def export_csv(
        self,
        output_directory,
        transactions,
        budgets,
        categories,
    ):
        transaction_file = (
            output_directory
            / "transactions.csv"
        )

        budget_file = (
            output_directory
            / "budgets.csv"
        )

        category_file = (
            output_directory
            / "categories.csv"
        )

        self.write_transactions_csv(
            transaction_file,
            transactions,
        )

        self.write_budgets_csv(
            budget_file,
            budgets,
        )

        self.write_categories_csv(
            category_file,
            categories,
        )

        return [
            transaction_file,
            budget_file,
            category_file,
        ]

    def write_transactions_csv(
        self,
        file_path,
        transactions,
    ):
        with file_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.writer(
                csv_file
            )

            writer.writerow(
                [
                    "id",
                    "type",
                    "description",
                    "amount",
                    "category",
                    "date",
                    "notes",
                    "created_at",
                    "updated_at",
                ]
            )

            for transaction in transactions:
                writer.writerow(
                    [
                        transaction.id,
                        transaction.transaction_type,
                        transaction.description,
                        f"{transaction.amount:.2f}",
                        (
                            transaction.category.name
                            if transaction.category
                            else ""
                        ),
                        transaction.date.isoformat(),
                        transaction.notes,
                        transaction.created_at.isoformat(),
                        transaction.updated_at.isoformat(),
                    ]
                )

    def write_budgets_csv(
        self,
        file_path,
        budgets,
    ):
        with file_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.writer(
                csv_file
            )

            writer.writerow(
                [
                    "id",
                    "category",
                    "amount",
                    "month",
                    "created_at",
                    "updated_at",
                ]
            )

            for budget in budgets:
                writer.writerow(
                    [
                        budget.id,
                        budget.category.name,
                        f"{budget.amount:.2f}",
                        budget.month.isoformat(),
                        budget.created_at.isoformat(),
                        budget.updated_at.isoformat(),
                    ]
                )

    def write_categories_csv(
        self,
        file_path,
        categories,
    ):
        with file_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.writer(
                csv_file
            )

            writer.writerow(
                [
                    "id",
                    "name",
                ]
            )

            for category in categories:
                writer.writerow(
                    [
                        category.id,
                        category.name,
                    ]
                )

    def export_json(
        self,
        output_directory,
        username,
        selected_month,
        transactions,
        budgets,
        categories,
    ):
        export_file = (
            output_directory
            / "expense_data.json"
        )

        data = {
            "export": {
                "username": username,
                "month": selected_month or "all",
            },
            "categories": [
                {
                    "id": category.id,
                    "name": category.name,
                }
                for category in categories
            ],
            "transactions": [
                {
                    "id": transaction.id,
                    "type": transaction.transaction_type,
                    "description": transaction.description,
                    "amount": transaction.amount,
                    "category": (
                        transaction.category.name
                        if transaction.category
                        else None
                    ),
                    "date": transaction.date,
                    "notes": transaction.notes,
                    "created_at": (
                        transaction.created_at.isoformat()
                    ),
                    "updated_at": (
                        transaction.updated_at.isoformat()
                    ),
                }
                for transaction in transactions
            ],
            "budgets": [
                {
                    "id": budget.id,
                    "category": budget.category.name,
                    "amount": budget.amount,
                    "month": budget.month,
                    "created_at": (
                        budget.created_at.isoformat()
                    ),
                    "updated_at": (
                        budget.updated_at.isoformat()
                    ),
                }
                for budget in budgets
            ],
        }

        with export_file.open(
            "w",
            encoding="utf-8",
        ) as json_file:
            json.dump(
                data,
                json_file,
                cls=DecimalEncoder,
                indent=4,
                ensure_ascii=False,
            )

        return [
            export_file,
        ]