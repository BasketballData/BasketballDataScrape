# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-16 11:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_auto_20170916_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='start_time',
            field=models.BigIntegerField(blank=True, default=0, null=True),
        ),
    ]
