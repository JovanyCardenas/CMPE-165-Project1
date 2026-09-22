from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from expenses.models import Budget, Category, Transaction


class Command(BaseCommand):
    help = "Checks Expense Tracker data for common integrity problems."

    def handle(self, *args, **options):
        problems = 0

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Expense Tracker Integrity Check"
            )
        )

        self.stdout.write("")
        self.stdout.write(
            "Checking transactions..."
        )

        invalid_amount_transactions = (
            Transaction.objects
            .filter(amount__lte=0)
            .count()
        )

        if invalid_amount_transactions:
            problems += invalid_amount_transactions

            self.stdout.write(
                self.style.ERROR(
                    f"Found {invalid_amount_transactions} "
                    f"transaction(s) with non-positive amounts."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Transaction amounts look valid."
                )
            )

        self.stdout.write("")
        self.stdout.write(
            "Checking budgets..."
        )

        invalid_budgets = (
            Budget.objects
            .filter(amount__lte=0)
            .count()
        )

        if invalid_budgets:
            problems += invalid_budgets

            self.stdout.write(
                self.style.ERROR(
                    f"Found {invalid_budgets} "
                    f"budget(s) with non-positive amounts."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Budget amounts look valid."
                )
            )

        duplicate_budgets = (
            Budget.objects
            .values(
                "user_id",
                "category_id",
                "month",
            )
            .annotate(
                count=Count("id")
            )
            .filter(
                count__gt=1
            )
        )

        duplicate_budget_count = (
            duplicate_budgets.count()
        )

        if duplicate_budget_count:
            problems += duplicate_budget_count

            self.stdout.write(
                self.style.ERROR(
                    f"Found {duplicate_budget_count} "
                    f"duplicate monthly budget group(s)."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "No duplicate monthly budgets found."
                )
            )

        self.stdout.write("")
        self.stdout.write(
            "Checking categories..."
        )

        category_mismatches = (
            Transaction.objects
            .filter(
                category__isnull=False
            )
            .exclude(
                user_id=(
                    # This cannot be expressed as a normal value
                    # comparison without F(), handled below.
                    0
                )
            )
        )

        from django.db.models import F

        category_mismatches = (
            Transaction.objects
            .filter(
                category__isnull=False
            )
            .exclude(
                user_id=F("category__user_id")
            )
            .count()
        )

        if category_mismatches:
            problems += category_mismatches

            self.stdout.write(
                self.style.ERROR(
                    f"Found {category_mismatches} transaction(s) "
                    f"using another user's category."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Transaction/category ownership is valid."
                )
            )

        budget_category_mismatches = (
            Budget.objects
            .exclude(
                user_id=F("category__user_id")
            )
            .count()
        )

        if budget_category_mismatches:
            problems += budget_category_mismatches

            self.stdout.write(
                self.style.ERROR(
                    f"Found {budget_category_mismatches} budget(s) "
                    f"using another user's category."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Budget/category ownership is valid."
                )
            )

        self.stdout.write("")
        self.stdout.write(
            "Database totals:"
        )

        self.stdout.write(
            f"  Categories: {Category.objects.count()}"
        )

        self.stdout.write(
            f"  Transactions: {Transaction.objects.count()}"
        )

        self.stdout.write(
            f"  Budgets: {Budget.objects.count()}"
        )

        self.stdout.write("")

        if problems:
            self.stdout.write(
                self.style.ERROR(
                    f"Integrity check completed with "
                    f"{problems} potential problem(s)."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Expense Tracker integrity check passed."
                )
            )