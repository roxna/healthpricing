# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 21:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0022_procedure_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='comments',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]