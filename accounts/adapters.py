from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter to populate profile data on Google login."""

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        try:
            extra_data = sociallogin.account.extra_data
            if hasattr(user, "profile"):
                profile = user.profile
                if not profile.full_name:
                    name = (
                        extra_data.get("name")
                        or f"{extra_data.get('given_name', '')} {extra_data.get('family_name', '')}".strip()
                    )
                    if name:
                        profile.full_name = name
                        profile.save(update_fields=["full_name"])
        except Exception:
            pass
        return user
