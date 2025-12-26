from allauth.account.forms import SignupForm as BaseSignupForm

from django import forms
from django.utils.translation import gettext_lazy as _


class SignupForm(BaseSignupForm):
    first_name = forms.CharField(
        label=_("First Name"),
        widget=forms.TextInput(
            attrs={"placeholder": _("First Name"), "autocomplete": "given-name"}
        ),
    )

    last_name = forms.CharField(
        label=_("Last Name"),
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": _("Last Name"), "autocomplete": "family-name"}
        ),
    )
