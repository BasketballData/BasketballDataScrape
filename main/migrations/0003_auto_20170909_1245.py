# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-09 12:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_game_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='status',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]