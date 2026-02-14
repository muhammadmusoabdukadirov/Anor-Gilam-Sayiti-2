from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from .models import VisitLog


class VisitLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Faqat asosiy sahifaga kirishlarni log qilamiz yoki barchasini
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            try:
                user = request.user if request.user.is_authenticated else None
                session_key = request.session.session_key

                # Har bir sessiya uchun kuniga bir marta log yozamiz
                today = timezone.now().date()
                start_of_day = timezone.make_aware(timezone.datetime(today.year, today.month, today.day))

                existing_log = VisitLog.objects.filter(
                    user=user,
                    session_key=session_key,
                    timestamp__gte=start_of_day
                ).exists()

                if not existing_log and session_key:
                    VisitLog.objects.create(
                        user=user,
                        session_key=session_key,
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        path=request.path
                    )
            except:
                pass  # Log qilishda xatolik bo'lsa ham ish davom etsin

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip