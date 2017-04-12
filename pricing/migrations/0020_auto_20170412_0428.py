# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 04:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0019_auto_20170412_0339'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='overall_score',
            field=models.IntegerField(choices=[(1, b'Really Bad'), (2, b'Below Average'), (3, b'Average'), (4, b'Above Average'), (5, b'Amazing')], default=5),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.IntegerField(blank=True, choices=[(1, 'Male'), (2, 'Female')], null=True),
        ),
    ]