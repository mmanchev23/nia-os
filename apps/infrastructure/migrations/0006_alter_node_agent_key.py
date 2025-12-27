import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("infrastructure", "0005_remove_uuid_null"),
    ]

    operations = [
        migrations.AlterField(
            model_name="node",
            name="agent_key",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text="Secret key used by the agent to authenticate.",
                unique=True,
                verbose_name="Agent Key",
            ),
        ),
    ]
