from .models import *

def feature_flags(request):
    flags = {ft.slug: ft.is_active for ft in FeatureToggle.objects.all()}
    return {"features": flags}

def admin_globals(request):
    active_banner = SiteBanner.objects.filter(is_active=True).first()
    return {
        "active_banner": active_banner,
        "is_impersonating": getattr(request, "is_impersonating", False),
        "original_user": getattr(request, "original_user", None),
    }

def user_settings(request):
    if request.user.is_authenticated:
        settings, _ = UserSettings.objects.get_or_create(
            user=request.user
        )

        return {
            "user_settings": settings
        }

    return {
        "user_settings": None
    }