from django import forms
from django.utils.translation import gettext_lazy as _

from unfold.widgets import UnfoldAdminPasswordWidget

from .models import Cluster, Node


class NodeAdminForm(forms.ModelForm):
    password = forms.CharField(
        label=_("Password"),
        required=False,
        widget=UnfoldAdminPasswordWidget(
            attrs={"placeholder": _("********"), "autocomplete": "new-password"}
        ),
        help_text=_(
            "The password is encrypted. Enter a new password to change it, or leave blank to keep the current one."
        ),
    )

    class Meta:
        model = Node
        fields = "__all__"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields["password"].required = True

    def save(self, commit=True) -> Node:
        instance = super().save(commit=False)

        password = self.cleaned_data.get("password")

        if password:
            instance.password = password
        elif instance.pk:
            original = Node.objects.get(pk=instance.pk)
            instance.password = original.password

        if commit:
            instance.save()

        return instance


class ClusterForm(forms.ModelForm):
    class Meta:
        model = Cluster
        fields = ["name", "summary"]


class NodeForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = ["cluster", "hostname", "ip_address", "username", "password", "port"]
        widgets = {
            "password": forms.PasswordInput(attrs={"autocomplete": "current-password"}),
        }

    def __init__(self, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["cluster"].queryset = Cluster.objects.filter(user=user)
