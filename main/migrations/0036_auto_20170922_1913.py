# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-22 19:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20170919_1139'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='actions',
            options={'ordering': ['-period', '-action_uid'], 'verbose_name': 'Action'},
        ),
        migrations.AddField(
            model_name='actions',
            name='action_local_uid',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
