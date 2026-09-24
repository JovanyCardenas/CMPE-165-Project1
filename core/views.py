from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from .models import *
from .signals import DEFAULT_TOGGLES
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.core.management import call_command

User = get_user_model()


# ADMINISTRATOR TOOLS
@staff_member_required
def admin_tools(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    system_setting = SystemSetting.load()
    banners = SiteBanner.objects.all().order_by("-created_at")
    recent_users = User.objects.exclude(id=request.user.id).order_by("-date_joined")[:15]

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "seed_default_toggles":
            created_count = 0
            for toggle_data in DEFAULT_TOGGLES:
                _, created = FeatureToggle.objects.get_or_create(
                    slug=toggle_data["slug"],
                    defaults={
                        "name": toggle_data["name"],
                        "is_active": toggle_data["is_active"],
                    },
                )
                if created:
                    created_count += 1
            messages.success(
                request,
                f"Default feature toggles synchronized. ({created_count} newly created)",
            )

        elif action == "update_maintenance":
            system_setting.maintenance_mode = "maintenance_mode" in request.POST
            system_setting.maintenance_message = request.POST.get("maintenance_message", "")
            system_setting.save()
            messages.success(request, "Maintenance settings updated.")

        # ... your existing banner actions ...

        elif action == "seed_demo_data":
            try:
                call_command("seed_demo_data")
                messages.success(
                    request,
                    "Demo account and sample data created successfully."
                )
            except Exception as e:
                messages.error(
                    request,
                    f"Demo setup failed: {e}"
                )

        elif action == "reset_demo_data":
            try:
                call_command("seed_demo_data", reset=True)
                messages.success(
                    request,
                    "Demo account reset successfully."
                )
            except Exception as e:
                messages.error(
                    request,
                    f"Demo reset failed: {e}"
                )

        elif action == "generate_sample_transactions":
            try:
                call_command(
                    "generate_sample_transactions",
                    "demo",
                    months=6,
                )
                messages.success(
                    request,
                    "Six months of sample transactions generated."
                )
            except Exception as e:
                messages.error(
                    request,
                    f"Sample generation failed: {e}"
                )

        elif action == "clear_demo_data":
            try:
                call_command("clear_demo_data")
                messages.success(
                    request,
                    "Demo financial data cleared."
                )
            except Exception as e:
                messages.error(
                    request,
                    f"Demo data could not be cleared: {e}"
                )

        elif action == "delete_demo_account":
            try:
                call_command("clear_demo_data", delete_user=True)
                messages.success(
                    request,
                    "Demo account and all associated data deleted."
                )
            except Exception as e:
                messages.error(
                    request,
                    f"Demo account could not be deleted: {e}"
                )

        elif action == "check_expense_tracker":
            try:
                call_command("check_expense_tracker")
                messages.success(
                    request,
                    "Expense Tracker integrity check completed."
                )
            except Exception as e:
                messages.error(
                    request,
                    f"Integrity check failed: {e}"
                )

        return redirect("admin_tools")

    return render(
        request,
        "admin/admin_tools.html",
        {
            "system_setting": system_setting,
            "banners": banners,
            "recent_users": recent_users,
        },
    )


@staff_member_required
def impersonate_user(request, user_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    target_user = get_object_or_404(User, id=user_id)

    # Store real superuser ID in session before login switch
    current_admin_id = request.session.get("_impersonator_id") or request.user.id
    login(request, target_user)
    request.session["_impersonator_id"] = current_admin_id

    messages.warning(request, f"You are now impersonating {target_user.username}.")
    return redirect("home")


def stop_impersonation(request):
    impersonator_id = request.session.get("_impersonator_id")
    if not impersonator_id:
        return redirect("home")

    admin_user = get_object_or_404(User, id=impersonator_id)
    login(request, admin_user)
    request.session.pop("_impersonator_id", None)

    messages.success(request, "Returned to your superuser account.")
    return redirect("admin_tools")

@staff_member_required
def feature_toggle(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        toggle_id = request.POST.get("toggle_id")
        toggle = FeatureToggle.objects.get(id=toggle_id)
        toggle.is_active = not toggle.is_active
        toggle.save()
        return redirect("feature_toggle")

    toggles = FeatureToggle.objects.all()
    return render(request, "admin/feature_toggle.html", {"toggles": toggles})




# NON ADMIN VIEWS
def coming_soon(request):
    return render(request, "coming_soon.html")

def home(request):
    return render(request, "pages/home.html")

def about(request):
    return render(request, "pages/about.html")

def contact(request):
    return render(request, "pages/contact.html")

def resources(request):
    return render(request, "coming_soon.html")
    # return render(request, "pages/resources.html")

# @login_required
# def settings(request):
#     return render(request, "coming_soon.html")
#     # return render(request, "pages/settings.html")

@login_required
def settings(request):
    user_settings, _ = UserSettings.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        user_settings.theme = request.POST.get(
            "theme", "system"
        )

        user_settings.currency = request.POST.get(
            "currency", "USD"
        )

        user_settings.dashboard_period = request.POST.get(
            "dashboard_period", "month"
        )

        user_settings.default_transaction_type = request.POST.get(
            "default_transaction_type", "expense"
        )

        user_settings.items_per_page = int(
            request.POST.get("items_per_page", 25)
        )

        user_settings.budget_warning_threshold = int(
            request.POST.get("budget_warning_threshold", 80)
        )

        user_settings.week_start = request.POST.get(
            "week_start", "sunday"
        )

        user_settings.hide_financial_amounts = (
            "hide_financial_amounts" in request.POST
        )

        user_settings.student_mode = (
            "student_mode" in request.POST
        )

        user_settings.save()

        messages.success(
            request,
            "Your settings have been saved."
        )

        return redirect("settings")

    return render(
        request,
        "pages/settings.html",
        {
            "settings": user_settings,
        },
    )

@login_required
def dashboard(request):
    return render(request, "expenses/dashboard.html")