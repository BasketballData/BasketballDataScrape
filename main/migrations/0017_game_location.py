# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-12 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_actions'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='location',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
