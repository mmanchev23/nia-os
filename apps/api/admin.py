from django.contrib import admin

from unfold.admin import ModelAdmin

from rest_framework.authtoken.models import Token, TokenProxy


admin.site.unregister(TokenProxy)


@admin.register(Token)
class TokenAdmin(ModelAdmin):
    pass
