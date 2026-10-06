from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect


class CorporateSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        data = sociallogin.account.extra_data
        email = (data.get("email") or "").lower()
        verified = data.get("email_verified", False)
        allowed = "@" + settings.ALLOWED_EMAIL_DOMAIN.lower()

        if not verified or not email.endswith(allowed):
            messages.error(
                request,
                f"Only {settings.ALLOWED_EMAIL_DOMAIN} accounts can log in.",
            )
            raise ImmediateHttpResponse(redirect("login"))