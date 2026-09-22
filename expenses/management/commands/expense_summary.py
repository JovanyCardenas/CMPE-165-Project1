from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from django.utils import timezone

from expenses.models import Transaction


User = get_user_model()


class Command(BaseCommand):
    help = "Displays a financial summary for an Expense Tracker user."

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            type=str,
            help="Username to generate the summary for.",
        )

        parser.add_argument(
            "--all-time",
            action="store_true",
            help="Show all-time totals instead of the current month.",
        )

    def handle(self, *args, **options):
        username = options["username"]

        try:
            user = User.objects.get(
                username=username
            )
        except User.DoesNotExist:
            raise CommandError(
                f'User "{username}" does not exist.'
            )

        transactions = Transaction.objects.filter(
            user=user
        )

        if not options["all_time"]:
            today = timezone.localdate()

            transactions = transactions.filter(
                date__year=today.year,
                date__month=today.month,
            )

            period = today.strftime("%B %Y")
        else:
            period = "All Time"

        income = (
            transactions
            .filter(
                transaction_type=Transaction.INCOME
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        expenses = (
            transactions
            .filter(
                transaction_type=Transaction.EXPENSE
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        net = income - expenses

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Expense Summary — {username}"
            )
        )

        self.stdout.write(
            f"Period: {period}"
        )

        self.stdout.write("")

        self.stdout.write(
            f"Income:       ${income:,.2f}"
        )

        self.stdout.write(
            f"Expenses:     ${expenses:,.2f}"
        )

        self.stdout.write(
            f"Net Cash Flow: ${net:,.2f}"
        )

        self.stdout.write(
            f"Transactions: {transactions.count()}"
        )