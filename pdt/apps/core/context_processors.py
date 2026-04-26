from django.conf import settings


def donation(request):
    return {
        "DONATION_URL": settings.DONATION_URL,
        "DONATION_LABEL": settings.DONATION_LABEL,
    }
