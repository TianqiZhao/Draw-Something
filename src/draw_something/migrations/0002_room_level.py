# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-17 04:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('draw_something', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='level',
            field=models.CharField(choices=[('e', 'Easy'), ('m', 'Medium'), ('h', 'Hard')], default='e', max_length=1),
        ),
    ]
