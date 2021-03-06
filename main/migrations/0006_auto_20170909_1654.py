# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-09 16:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20170909_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='team_a',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_team_a', to='main.Team'),
        ),
        migrations.AlterField(
            model_name='game',
            name='team_b',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_team_b', to='main.Team'),
        ),
    ]
