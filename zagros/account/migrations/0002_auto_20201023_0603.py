# Generated by Django 3.1.2 on 2020-10-23 02:33

from django.db import migrations, models
import django.utils.crypto
import zagros.core.utils.json_serializer


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='jwt_token_key',
            field=models.CharField(default=django.utils.crypto.get_random_string, max_length=12),
        ),
        migrations.AlterField(
            model_name='user',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, encoder=zagros.core.utils.json_serializer.CustomJsonEncoder, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='private_metadata',
            field=models.JSONField(blank=True, default=dict, encoder=zagros.core.utils.json_serializer.CustomJsonEncoder, null=True),
        ),
    ]
