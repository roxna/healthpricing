# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 23:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0023_lead_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=40, null=True)),
                ('source', models.IntegerField(choices=[(1, 'Blog'), (2, 'Testimonial'), (3, 'Contact Form'), (4, 'Newsletter')], default=2, max_length=40)),
                ('title', models.CharField(blank=True, max_length=40, null=True)),
                ('company', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('summary', models.TextField()),
                ('content', models.TextField()),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('image', models.ImageField(blank=True, null=True, upload_to=b'')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blogs', to='pricing.Author')),
            ],
        ),
        migrations.CreateModel(
            name='ContactRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.IntegerField(choices=[(1, 'How Does It Work?'), (2, 'Booking Appointments'), (3, 'Partnerships'), (0, 'Other')], max_length=15)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('body', models.TextField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact_requests', to='pricing.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=40, null=True)),
                ('comments', models.CharField(max_length=250)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='testimonials', to='pricing.Author')),
            ],
        ),
        migrations.RenameField(
            model_name='review',
            old_name='author',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='lead',
            name='service',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='leads', to='pricing.Service'),
            preserve_default=False,
        ),
    ]
