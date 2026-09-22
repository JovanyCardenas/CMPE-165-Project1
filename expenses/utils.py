from .models import Category


DEFAULT_CATEGORIES = [
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


def ensure_default_categories(user):
    if Category.objects.filter(user=user).exists():
        return

    Category.objects.bulk_create(
        [
            Category(user=user, name=name)
            for name in DEFAULT_CATEGORIES
        ]
    )