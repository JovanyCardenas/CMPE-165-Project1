from django import forms

from .models import *
from datetime import date
from django.utils import timezone


INPUT_CLASSES = (
    "block w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 "
    "text-sm text-slate-900 shadow-sm outline-none transition "
    "placeholder:text-slate-400 focus:border-indigo-500 "
    "focus:ring-2 focus:ring-indigo-500/20"
)

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction

        fields = [
            "transaction_type",
            "description",
            "amount",
            "category",
            "date",
            "notes",
        ]

        widgets = {
            "transaction_type": forms.Select(
                attrs={"class": INPUT_CLASSES}
            ),

            "description": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "e.g. Groceries",
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "0.00",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),

            "category": forms.Select(
                attrs={"class": INPUT_CLASSES}
            ),

            "date": forms.DateInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "type": "date",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 4,
                    "placeholder": "Optional notes...",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.fields["category"].queryset = (
                Category.objects
                .filter(user=user)
                .order_by("name")
            )


class BudgetForm(forms.ModelForm):

    month = forms.ChoiceField(
        label="Month",
        widget=forms.Select(
            attrs={
                "class": INPUT_CLASSES,
            }
        ),
    )

    class Meta:
        model = Budget

        fields = [
            "category",
            "amount",
            "month",
        ]

        widgets = {
            "category": forms.Select(
                attrs={
                    "class": INPUT_CLASSES,
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "min": "0.01",
                    "step": "0.01",
                    "placeholder": "0.00",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        today = timezone.localdate()

        # Create month choices:
        # 12 months before current month through
        # 24 months after current month.
        choices = []

        for offset in range(-12, 25):
            year = today.year
            month = today.month + offset

            while month > 12:
                month -= 12
                year += 1

            while month < 1:
                month += 12
                year -= 1

            month_date = date(year, month, 1)

            choices.append(
                (
                    month_date.strftime("%Y-%m"),
                    month_date.strftime("%B %Y"),
                )
            )

        self.fields["month"].choices = choices

        # New budget defaults to current month
        if not self.is_bound and not self.instance.pk:
            self.initial["month"] = today.strftime("%Y-%m")

        # Editing an existing budget
        elif not self.is_bound and self.instance.pk:
            self.initial["month"] = self.instance.month.strftime("%Y-%m")

        # Only show categories belonging to this user
        if user:
            self.fields["category"].queryset = (
                Category.objects
                .filter(user=user)
                .order_by("name")
            )

    def clean_month(self):
        month_value = self.cleaned_data["month"]

        year, month = map(
            int,
            month_value.split("-")
        )

        return date(year, month, 1)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "e.g. Travel",
                    "maxlength": "100",
                    "autofocus": True,
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError("Enter a category name.")

        if self.user:
            existing = Category.objects.filter(
                user=self.user,
                name__iexact=name,
            )

            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise forms.ValidationError(
                    "You already have a category with this name."
                )

        return name