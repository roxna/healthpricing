# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 23:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0024_auto_20170412_2313'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contactrequest',
            old_name='body',
            new_name='comments',
        ),
        migrations.AlterField(
            model_name='contactrequest',
            name='topic',
            field=models.IntegerField(choices=[(1, b'How Does It Work?'), (2, b'Booking Appointments'), (3, b'Partnerships'), (0, b'Other')], default=0),
        ),
    ]
