from django import forms
from django.utils.translation import gettext_lazy as _

from apps.infrastructure.models import Cluster, Node


class JobForm(forms.Form):
    name = forms.CharField(label=_("Job Name"), max_length=128)

    command = forms.CharField(
        label=_("Command"),
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text=_("Bash command to execute"),
    )

    target_node = forms.ModelChoiceField(
        queryset=Node.objects.none(), required=False, label=_("Target Node")
    )

    target_cluster = forms.ModelChoiceField(
        queryset=Cluster.objects.none(), required=False, label=_("Target Cluster")
    )

    schedule_type = forms.ChoiceField(
        choices=[
            ("O", _("Run Once")),
            ("I", _("Recurring (Minutes)")),
            ("H", _("Hourly")),
            ("D", _("Daily")),
        ],
        label=_("Frequency"),
    )

    minutes = forms.IntegerField(
        required=False,
        min_value=1,
        label=_("Interval (Minutes)"),
        help_text=_('Only required if "Recurring" is selected'),
    )

    def __init__(self, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["target_node"].queryset = Node.objects.filter(cluster__user=user)
        self.fields["target_cluster"].queryset = Cluster.objects.filter(user=user)

    def clean(self) -> dict:
        cleaned_data = super().clean()
        node = cleaned_data.get("target_node")
        cluster = cleaned_data.get("target_cluster")
        stype = cleaned_data.get("schedule_type")
        mins = cleaned_data.get("minutes")

        if node and cluster:
            raise forms.ValidationError(
                _("Please select either a Node OR a Cluster, not both.")
            )

        if not node and not cluster:
            raise forms.ValidationError(_("Please select a target (Node or Cluster)."))

        if stype == "I" and not mins:
            self.add_error("minutes", _("Please specify the number of minutes."))

        return cleaned_data
