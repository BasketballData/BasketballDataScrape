# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-19 09:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20170919_0923'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='init_scrape',
            field=models.BooleanField(default=False),
        ),
    ]
