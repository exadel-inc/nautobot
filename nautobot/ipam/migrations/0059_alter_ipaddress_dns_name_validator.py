from django.db import migrations, models

import nautobot.ipam.validators


class Migration(migrations.Migration):
    dependencies = [
        ("ipam", "0058_iprange_role_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ipaddress",
            name="dns_name",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, validators=[nautobot.ipam.validators.DNSValidator]
            ),
        ),
    ]
