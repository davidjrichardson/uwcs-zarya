# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-17 12:41
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0021_eventpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventpage',
            name='description',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='finish',
            field=models.DateTimeField(default=datetime.datetime(2016, 9, 17, 13, 41, 52, 192769)),
        ),
    ]
