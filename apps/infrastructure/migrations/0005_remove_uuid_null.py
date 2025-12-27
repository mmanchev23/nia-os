import uuid
from django.db import migrations


def gen_uuid(apps, schema_editor):
    Node = apps.get_model("infrastructure", "Node")
    for row in Node.objects.all():
        row.agent_key = uuid.uuid4()
        row.save(update_fields=["agent_key"])


class Migration(migrations.Migration):
    dependencies = [
        ("infrastructure", "0004_node_agent_key_node_last_seen_node_status"),
    ]

    operations = [
        # Python code to generate unique UUIDs for existing rows
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
