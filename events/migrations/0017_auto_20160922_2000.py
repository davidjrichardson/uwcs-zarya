# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-22 20:00
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_auto_20160922_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventpage',
            name='finish',
            field=models.DateTimeField(default=datetime.datetime(2016, 9, 22, 21, 0, 15, 711866, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='signup_close',
            field=models.DateTimeField(default=datetime.datetime(2016, 9, 22, 21, 0, 15, 711945, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='eventsignup',
            name='comment',
            field=models.CharField(blank=True, max_length=1024),
        ),
    ]
