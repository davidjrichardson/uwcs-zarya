# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-24 19:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0019_eventsindexpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutpage',
            name='full_title',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]