from allauth.account.signals import user_signed_up
from django.dispatch import receiver


@receiver(user_signed_up)
def social_login_fname_lname_profilepic(sociallogin, user, **kwargs):

    if sociallogin:
        if sociallogin.account.provider == "google":
            avatar = sociallogin.account.extra_data["picture"]
            user.avatar = avatar

    user.save()
