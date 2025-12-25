from django.http import HttpResponse
from django.shortcuts import render

from config.middlewares.htmx import HttpRequest


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "core/index.html")
