# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-30 21:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('draw_something', '0004_auto_20171128_0047'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='start',
            field=models.BooleanField(default=False),
        ),
    ]
