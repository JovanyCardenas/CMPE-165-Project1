from django.contrib import admin
from django.db.models import Count

from .models import Budget, Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "transaction_count",
        "budget_count",
    )

    search_fields = (
        "name",
        "user__username",
        "user__email",
    )

    list_filter = (
        "user",
    )

    ordering = (
        "user__username",
        "name",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.annotate(
            _transaction_count=Count(
                "transactions",
                distinct=True,
            ),
            _budget_count=Count(
                "budgets",
                distinct=True,
            ),
        )

    @admin.display(
        description="Transactions",
        ordering="_transaction_count",
    )
    def transaction_count(self, obj):
        return obj._transaction_count

    @admin.display(
        description="Budgets",
        ordering="_budget_count",
    )
    def budget_count(self, obj):
        return obj._budget_count


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "user",
        "transaction_type",
        "formatted_amount",
        "category",
        "date",
    )

    list_filter = (
        "transaction_type",
        "category",
        "date",
    )

    search_fields = (
        "description",
        "notes",
        "user__username",
        "user__email",
        "category__name",
    )

    ordering = (
        "-date",
        "-created_at",
    )

    date_hierarchy = "date"

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "user",
        "category",
    )

    @admin.display(
        description="Amount",
        ordering="amount",
    )
    def formatted_amount(self, obj):
        prefix = "+" if obj.transaction_type == Transaction.INCOME else "-"
        return f"{prefix}${obj.amount:,.2f}"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "user",
        "formatted_amount",
        "month",
        "created_at",
    )

    list_filter = (
        "month",
        "category",
    )

    search_fields = (
        "category__name",
        "user__username",
        "user__email",
    )

    ordering = (
        "-month",
        "category__name",
    )

    date_hierarchy = "month"

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "user",
        "category",
    )

    @admin.display(
        description="Budget Amount",
        ordering="amount",
    )
    def formatted_amount(self, obj):
        return f"${obj.amount:,.2f}"