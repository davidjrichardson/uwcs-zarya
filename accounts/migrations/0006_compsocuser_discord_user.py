# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-05 21:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20171002_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='compsocuser',
            name='discord_user',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
