# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 01:43
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0015_auto_20170412_0031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='overall_score',
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='consultation_fee',
            field=models.IntegerField(default=100, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lead',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leads', to='pricing.Service'),
        ),
    ]