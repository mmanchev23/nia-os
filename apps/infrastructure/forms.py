from django import forms

from .models import Cluster, Node


class ClusterForm(forms.ModelForm):
    class Meta:
        model = Cluster
        fields = ["name", "summary"]


class NodeForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = ["cluster", "hostname", "ip_address", "username", "password", "port"]
        widgets = {
            "password": forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        }

    def __init__(self, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["cluster"].queryset = Cluster.objects.filter(user=user)
