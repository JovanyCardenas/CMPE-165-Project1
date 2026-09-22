from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense_categories",
    )
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_category_per_user",
            )
        ]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    INCOME = "income"
    EXPENSE = "expense"

    TRANSACTION_TYPES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        default=EXPENSE,
    )

    description = models.CharField(max_length=200)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    date = models.DateField(
        default=timezone.localdate,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.description} - ${self.amount}"


class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    month = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-month", "category__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category", "month"],
                name="unique_monthly_category_budget",
            )
        ]

    def __str__(self):
        return f"{self.category.name} - ${self.amount}"