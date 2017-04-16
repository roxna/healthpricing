# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 19:22
from __future__ import unicode_literals

from django.db import migrations, models
import pricing.models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0021_auto_20170412_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='procedure',
            name='image',
            field=models.ImageField(blank=True, default='defaults/procedure.jpeg', null=True, upload_to=pricing.models.procedure_img_directory_path),
        ),
    ]