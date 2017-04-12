# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-07 23:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0003_auto_20170407_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zipcode',
            name='clinic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='zipcode', to='pricing.Clinic'),
        ),
    ]