from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
    GroupAdmin as BaseGroupAdmin,
)
from django.contrib.auth.models import Group

from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from django.contrib.sites.models import Site

from allauth.account.admin import EmailAddressAdmin as BaseEmailAddressAdmin
from allauth.account.models import EmailAddress

from allauth.socialaccount.admin import (
    SocialAccountAdmin as BaseSocialAccountAdmin,
    SocialTokenAdmin as BaseSocialTokenAdmin,
    SocialAppAdmin as BaseSocialAppAdmin,
)
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User


admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.unregister(EmailAddress)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)


class GroupProxy(Group):
    class Meta:
        proxy = True
        verbose_name = Group._meta.verbose_name
        verbose_name_plural = Group._meta.verbose_name_plural


class SiteProxy(Site):
    class Meta:
        proxy = True
        verbose_name = Site._meta.verbose_name
        verbose_name_plural = Site._meta.verbose_name_plural


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(GroupProxy)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(SiteProxy)
class SiteAdmin(BaseSiteAdmin, ModelAdmin):
    pass


@admin.register(EmailAddress)
class EmailAddressAdmin(BaseEmailAddressAdmin, ModelAdmin):
    pass


@admin.register(SocialAccount)
class SocialAccountAdmin(BaseSocialAccountAdmin, ModelAdmin):
    pass


@admin.register(SocialToken)
class SocialTokenAdmin(BaseSocialTokenAdmin, ModelAdmin):
    pass


@admin.register(SocialApp)
class SocialAppAdmin(BaseSocialAppAdmin, ModelAdmin):
    pass
