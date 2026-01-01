from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from rest_framework.authtoken.models import Token

from config.middlewares.htmx import HttpRequest


@method_decorator(login_required, name="dispatch")
class TokenDashboardView(View):
    template_name = "api/tokens.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        token, _ = Token.objects.get_or_create(user=request.user)

        context = {
            "token": token,
            "request": request,
        }

        return render(request, self.template_name, context)


@login_required
@require_POST
def rotate_token(request: HttpRequest) -> HttpResponse:
    try:
        Token.objects.filter(user=request.user).delete()
        new_token = Token.objects.create(user=request.user)

        if request.headers.get("HX-Request"):
            context = {"token": new_token, "request": request}
            return render(request, "api/tokens.html#oob_update", context)

        messages.success(request, _("Your API token has been successfully rotated."))
    except Exception:
        if not request.headers.get("HX-Request"):
            messages.error(request, _("An error occurred."))

    return redirect("api:tokens")
