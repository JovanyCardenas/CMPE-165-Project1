from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import FeatureToggle, SystemSetting

DEFAULT_TOGGLES = [
    {
        "name": "Budget Management",
        "slug": "enable_budgets",
        "is_active": True,
    },
    {
        "name": "Financial Reports & Insights",
        "slug": "enable_reports",
        "is_active": True,
    },
    {
        "name": "Transaction Filtering & Search",
        "slug": "enable_transaction_filters",
        "is_active": True,
    },
    {
        "name": "Financial Dashboard",
        "slug": "enable_financial_dashboard",
        "is_active": True,
    },
    {
        "name": "Spending Analytics",
        "slug": "enable_spending_analytics",
        "is_active": True,
    },
    {
        "name": "Recurring Transactions",
        "slug": "enable_recurring_transactions",
        "is_active": False,
    },
    {
        "name": "Savings Goals",
        "slug": "enable_savings_goals",
        "is_active": False,
    },
    {
        "name": "Receipt Uploads",
        "slug": "enable_receipt_uploads",
        "is_active": False,
    },
    {
        "name": "Bank Account Integration",
        "slug": "enable_bank_integration",
        "is_active": False,
    },
    {
        "name": "AI Financial Insights",
        "slug": "enable_ai_insights",
        "is_active": False,
    },
]

@receiver(post_migrate)
def initialize_system_defaults(sender, **kwargs):
    # Only run once for the core app
    if sender.name != "core":
        return

    # Ensure SystemSetting singleton exists
    SystemSetting.load()

    # Seed default toggles safely using get_or_create
    for toggle_data in DEFAULT_TOGGLES:
        FeatureToggle.objects.get_or_create(
            slug=toggle_data["slug"],
            defaults={
                "name": toggle_data["name"],
                "is_active": toggle_data["is_active"],
            },
        )