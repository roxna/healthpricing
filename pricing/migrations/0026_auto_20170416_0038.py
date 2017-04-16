# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-16 00:38
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0025_auto_20170412_2319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='gender',
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='gender',
            field=models.IntegerField(blank=True, choices=[(1, 'Male'), (2, 'Female')], null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='source',
            field=models.IntegerField(choices=[(1, 'Blog'), (2, 'Testimonial'), (3, 'Contact Form'), (4, 'Newsletter')], default=2),
        ),
        migrations.AlterField(
            model_name='doctorprofile',
            name='consultation_fee',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='doctorprofile',
            name='title',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
