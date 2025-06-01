from django.utils import timezone
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from myapp.models import SystemSetting

class SystemSettingExpirationMiddleware:
    """
    Middleware to check if the active SystemSetting has expired (after 1 minute).
    If expired, deactivate the setting and block access.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            setting = SystemSetting.objects.filter(is_active=True).order_by('-created_at').first()
            if setting:
                # Automatically compute expiration time as 1 minute after creation
                expiration_time = setting.created_at + timezone.timedelta(minutes=1)
                if timezone.now() > expiration_time:
                    setting.is_active = False
                    setting.save()
                    from django.contrib import messages
                    messages.warning(request, "System setting has expired. Access is now disabled.")
                    return HttpResponseForbidden("System is expired. Please contact admin.")
        except Exception as e:
            # Log error or handle it gracefully
            pass

        return self.get_response(request)
