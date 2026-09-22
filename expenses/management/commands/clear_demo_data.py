from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from expenses.models import Budget, Transaction


User = get_user_model()


DEMO_USERNAME = "demo"
DEMO_NOTE = "[DEMO DATA]"


class Command(BaseCommand):
    help = "Removes generated Expense Tracker demo financial data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete-user",
            action="store_true",
            help="Also delete the demo user account.",
        )

    def handle(self, *args, **options):
        try:
            user = User.objects.get(
                username=DEMO_USERNAME
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    "Demo user does not exist."
                )
            )
            return

        if options["delete_user"]:
            user.delete()

            self.stdout.write(
                self.style.SUCCESS(
                    "Demo user and all associated data deleted."
                )
            )

            return

        transaction_count, _ = (
            Transaction.objects
            .filter(
                user=user,
                notes__contains=DEMO_NOTE,
            )
            .delete()
        )

        budget_count, _ = (
            Budget.objects
            .filter(user=user)
            .delete()
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo financial data cleared."
            )
        )

        self.stdout.write(
            f"Deleted transaction records: "
            f"{transaction_count}"
        )

        self.stdout.write(
            f"Deleted budget records: "
            f"{budget_count}"
        )

        self.stdout.write(
            "The demo user and categories were preserved."
        )