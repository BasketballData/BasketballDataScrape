# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-13 17:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SwissGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league_id', models.IntegerField()),
                ('competition_id', models.IntegerField()),
                ('match_id', models.IntegerField()),
                ('match_status', models.CharField(max_length=50)),
                ('match_time_utc', models.DateTimeField()),
                ('live', models.IntegerField()),
                ('home_name', models.CharField(max_length=300)),
                ('home_code', models.CharField(max_length=30)),
                ('home_team_id', models.IntegerField()),
                ('home_logo', models.CharField(max_length=300)),
                ('away_name', models.CharField(max_length=300)),
                ('away_code', models.CharField(max_length=30)),
                ('away_team_id', models.IntegerField()),
                ('away_logo', models.CharField(max_length=300)),
            ],
        ),
    ]
